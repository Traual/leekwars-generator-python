# Building a "god-tier" Python AI for the Leek Wars engine

This is a design memo: numbers, options, tradeoffs, and a recommended
roadmap. It deliberately stays grounded in the **measured cost of one
simulation** because that single number drives every design decision below.

---

## 1. How fast is the engine today?

Measured with `bench.py` / `bench_parallel.py` / `bench_search.py` /
`bench_search_parallel.py` (CPython 3.14, no JIT). All numbers are with
the optimised engine (Java parity 51/51 byte-for-byte preserved).

### Full fight throughput (basic AI vs basic AI)

| Metric | Baseline | Optimised | Gain |
|---|---|---|---|
| Single core | 93 fights/s | **158 fights/s** | +71 % |
| 12 cores | 427 fights/s | **622 fights/s** | +46 % |
| Per fight | 10.7 ms | 6.3 ms | -41 % |
| Average fight length | 43 turns, 541 actions | same | — |

### BFS-dim-1 hot path (clone + apply one action + read result)

This is the primitive the search loop calls 50–200 times per decision.

| Metric | Baseline | Optimised |
|---|---|---|
| State clone alone | 17.0 µs | **12.7 µs** |
| Clone + setWeapon + useWeapon + read | 28.2 µs | **17.5 µs**  (57 k evals/s/core) |
| Clone + moveEntity + read | 25.6 µs | 19.9 µs  (50 k evals/s/core) |
| 12-core scaling | — | **271 k evals/s** parallel |

### Other primitives

| | |
|---|---|
| RNG draw | 633 ns |
| A* pathfinding | ~110 µs/call (was 210 µs before A* rewrite) |

`cProfile` of 100 fights (basic-AI vs basic-AI):

```
fight.startTurn        2.46s   79%
  runTurn (AI)         2.16s   70%
    moveToward         0.97s     31%   ← getAStarPath = 0.83s
    useWeapon          0.95s     30%
      applyOnCell      0.55s
        Effect.apply   0.25s
initFight              0.59s   19%   (one-shot: map gen + composantes)
```

**Take-aways**
- A single full fight runs in 6 ms — fast enough that **self-play training
  data generation is no longer a bottleneck**: 158 fights/s × ~80
  decisions/fight = ~12 600 (state, action) samples/sec/core, ~150 k/s
  on 12 cores. A million-sample dataset in ≈ 7 seconds of wall time.
- A BFS-dim-1 decision (try every candidate action, score each) costs
  100 × 17.5 µs ≈ **1.75 ms/decision** on a single core, or ~150 µs on
  12 cores in parallel. If your NN scorer takes 100 µs (small MLP on
  GPU, batched), a full BFS-dim-1 turn is well under 2 ms — fits in any
  real-time budget.
- For deeper search (multi-turn MCTS with 1000+ rollouts) the
  simulator is still the bottleneck. That's where PyPy / Cython / Rust
  start to make sense (see §3).
- Map generation takes ~3 ms once per fight. For BFS that's amortised
  across all candidate evaluations — basically free.

---

## 2. The algorithmic ladder

Ordered from cheapest to most ambitious. Each step is a useful AI on its
own — you can stop wherever the strength is good enough for your goal.

### A. Hand-crafted heuristic (1-2 day effort, no GPU, no training)

A score function over `(state, candidate_move)` and a 1-ply argmax. Score
mixes:
- expected damage dealt this turn
- expected damage suffered if enemy plays its best counter
- positioning (LoS, distance to optimal weapon range, escape routes)
- chip cooldown management, TP/MP economy

**Estimated strength**: beats the current `basic_ai` without contest;
matches a serious mid-tier ladder bot. Already beats most level <200 AIs
on the official ladder if the heuristics are decent.

**Pros**: trivial to implement, transparent (you can reason about every
decision), runs in <1 ms/turn so it's a great teacher for distillation
later. **Cons**: ceiling is human-coded heuristic quality.

### B. Minimax with heuristic eval (≤ 1 ply, alpha-beta, move ordering)

Tree of `(your turn → opponent turn)`, prune with α-β, evaluate leaves
with the heuristic of (A). Branching factor is huge in Leek Wars
(≈ 50–200 reasonable moves/turn), so **expect to stay at depth 2** unless
you aggressively prune the action space.

**Speed-up tricks that matter**:
- **Action pruning**: only consider moves that reach a "useful" cell
  (within max weapon range of the enemy, or LoS-blocking, or healing
  spots). Drops branching from ~200 to ~15.
- **Killer moves / hash table**: standard.

**Estimated strength**: clear improvement over (A) on tactical positions
(2-shot kills, kite/peek). Gets crushed by anything stochastic (chip
crits, LoS RNG via map gen).

### C. MCTS with the existing simulator (UCT, no NN)

Run `N` rollouts per turn, each a random / heuristic playout to terminal.
Backprop wins/losses up the tree.

**Cost reality check**: a full rollout from a mid-fight state ≈ 5 ms (half
a fight). Budget 1 s per decision → 200 rollouts. UCT typically needs
**10⁴-10⁶** rollouts to be strong; we'd be 100× short.

So pure MCTS on the current sim is **not competitive** without one of:

1. **Faster sim** (see §3).
2. **Heuristic rollouts** (use (A) instead of random play): same number
   of rollouts but each one is much more informative.
3. **Truncated rollouts with NN value head** (see (D)).

### D. AlphaZero-lite — MCTS + neural value/policy net

The standard recipe for two-player perfect-info games when search alone
is too slow.

- **Network**: small MLP or tiny ResNet. Input: encoded `(map, both
  entities' stats, effects, cooldowns, current TP/MP)` → 2-3k features.
  Output: `(policy over actions, scalar value)`.
- **MCTS**: at each leaf, instead of rollout, query the net for value;
  use the policy as a prior on which actions to expand.
- **Training**: self-play. The Python sim *is* the environment.

**This is where the GPU earns its keep**: forward passes for batched
leaf-node evaluation. A 4-layer 256-wide MLP runs 10k inferences/s on
CPU, ~1M/s on a mid-range GPU.

**Compute budget reality**:
- 100-200 self-play games × 30 turns = 3-6k decisions/iteration
- Each decision = MCTS with ~200 simulations
- → ~10⁶ NN forward passes per training iteration
- Several hundred iterations needed for anything good

With our 427 fights/sec sim, generating one self-play iteration takes
~1 minute, and 200 iterations is ~3 hours — *if* the sim is the only
cost. In practice MCTS overhead and GPU sync bring it to a day. Doable.

**Estimated strength**: meaningfully better than (B); ceiling much
higher; behaviour is hard to interpret.

### E. Distillation back to LeekScript

Train the AlphaZero policy/value net (D), then **distill** it into
something that fits in 20M operations:

1. Generate `(state, best_move)` pairs from (D).
2. Fit a *much* smaller model (decision tree, k-NN over state features,
   or a hand-tuned heuristic that you tune by gradient on those labels).
3. Re-implement the small model in LeekScript.

This is the answer to your "use the perfect AI to train my LeekScript
AI" question. The Python AI plays the role of an oracle; the LeekScript
AI is what actually races on the ladder.

---

## 3. Making the simulator faster

If you're going to do (C/D), this is the *single* highest-ROI engineering
work. Options, ordered by effort vs. payoff:

| Option | Effort | Speedup | Catch |
|---|---|---|---|
| ~~Cache A* paths within a turn~~ | done | +38 % | invalidated on entity move |
| ~~Pre-computed cell adjacency~~ | done | small | one tuple lookup vs 4 method calls |
| ~~A\* rewrite (no per-call reset, local dicts)~~ | done | included | LIFO tie-break preserves Java behaviour |
| ~~`__slots__` + Stats as 18-int list + Map topology cache~~ | done | included | — |
| ~~Lift inline imports out of hot paths~~ | done | small | importlib.parent traversal cost |
| `multiprocessing.Pool` (already wired) | 1 hour | **~4×** | only for batch; intra-MCTS-tree won't scale this way |
| **PyPy** instead of CPython | 1 day | 5-10× per core | need to ensure no CPython-only deps; Flask/Numpy may complain |
| **Cython** the hot loops | 2-3 days | 5-15× on hot paths | A*, useWeapon, applyOnCell are good targets |
| **Numba** `@njit` on A* + cell math | 2-3 days | 10-50× on those funcs | Numba doesn't love OOP — would need a flat-array re-export of Map |
| Re-implement engine in **Rust + PyO3** | 1-2 weeks | **50-200×** | Big rewrite, but parity tests still apply (51/51) |
| **Vectorized batch sim** (NumPy) | 1-2 weeks | per-batch 100×+ | Hard for stateful sim; only works if rollouts share structure |

The realistic sweet-spot for a hobby project is **PyPy + A* cache + a tiny
Cython rewrite of `Map.getAStarPath`**, which together get you to
~5000-10000 fights/sec single-core. With 12 cores that's 50k+ fights/sec
— enough that AlphaZero-lite training fits in a few days.

---

## 4. Where the GPU actually helps

| Workload | GPU helps? | Why |
|---|---|---|
| Game simulation | ❌ | Branchy, OOP, integer-heavy. CPU wins. |
| Pathfinding (A*) | ❌ | Same — single-instance graph search. |
| Heuristic eval (a few floats) | ❌ | Latency-bound. CPU faster. |
| **NN forward pass on a batch of states** | ✅ | What modern game AIs use the GPU for. |
| **Backprop / training the NN** | ✅ | Standard PyTorch story. |
| **Batched MCTS leaf eval** | ✅ | Cluster pending leaves → one GPU forward. |

So: write the engine and the search in CPython/Cython/Rust, and use the
GPU exclusively for the neural network in approach (D).

---

## 5. Recommended roadmap

If the goal is "a perfect-ish Python AI to benchmark my LeekScript AI
against and to distill back into LeekScript heuristics", I'd do this in
order:

1. **Cache A\* + multiprocessing harness** — 1 day, no algorithmic
   change. Gets training data generation to a usable speed.
2. **Hand-crafted heuristic AI (A)** — 1 week. Becomes the "strong
   baseline" both for benchmarking and for guiding rollouts in (C/D).
3. **Heuristic-rollout MCTS (C)** with action pruning — 1 week. Already
   beats the heuristic on tactical positions if budget ≥ 1s/turn.
4. **PyPy port + Cython on `Map`** — 2-3 days. Brings sim under 1 ms;
   makes (D) realistic.
5. **AlphaZero-lite (D)** — multiple weeks of training, but the code is
   well-trodden (see [muzero-general](https://github.com/werner-duvaud/muzero-general),
   [alpha-zero-general](https://github.com/suragnair/alpha-zero-general)).
6. **Distillation to LeekScript (E)** — once (D) is strong enough.

You can stop after step 3 and have a Python AI that demolishes anything
on the ladder. (D) is for the absolute ceiling and for principled
learning of *why* a move is good (the value head).

---

## 6. What this would look like in the repo

Concrete file/module layout when (some of) the above is in place:

```
leekwars/                   ← engine (untouched, byte-for-byte parity)
ai/
├── heuristic.py            ← step 2: hand-crafted strong baseline
├── search/
│   ├── minimax.py          ← step 2-3: pruned α-β
│   └── mcts.py             ← step 3-4: UCT, heuristic rollouts, NN-guided
├── nn/
│   ├── encoder.py          ← state → tensor
│   ├── model.py            ← policy + value heads
│   └── train.py            ← self-play loop
├── distill/
│   └── to_leekscript.py    ← step 5
└── benchmarks/
    └── duel.py             ← run AI A vs AI B over N seeds, report winrate
bench.py, bench_parallel.py, profile_fight.py     ← already in repo
```

The benchmark harness (`ai/benchmarks/duel.py`) is the most important
*infrastructure* piece: it lets you compare two AIs on a fixed pool of
seeds and answer "is the new version actually better?" without
hand-waving.

---

## TL;DR

- Python sim runs at ~100 fights/sec/core (~430 with 12 cores). Plenty
  for batch training, **too slow for raw MCTS without speed-ups**.
- The realistic "god-tier" stack is: **strong heuristic → MCTS guided by
  that heuristic → eventually an AlphaZero-lite NN evaluated on GPU**.
- The single highest-ROI engineering item is making the simulator faster
  (cache A*, PyPy, or Cython). Without that, deep search isn't
  competitive.
- The GPU only helps once you have a neural value/policy head. Don't
  build a "GPU simulator" — that's a multi-month rewrite for marginal
  gains.
- For your stated end-goal (better LeekScript AI), the Python AI's job
  is to be a **teacher** you distill from, not the production ladder
  bot. Plan for that distillation step from day one.
