// Front-end for the leekwars Python sandbox.
const canvas = document.getElementById('board');
const ctx = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;

let state = null;
let cellsById = new Map();
let cellSize = { w: 28, h: 14 };  // diamond half-width/height
let originX = 0, originY = 0;
let hoverCell = null;

const els = {
    newGame: document.getElementById('new-game'),
    seed: document.getElementById('seed-label'),
    cards: document.getElementById('entity-cards'),
    weapons: document.getElementById('weapon-list'),
    chips: document.getElementById('chip-list'),
    status: document.getElementById('action-status'),
    endTurn: document.getElementById('end-turn'),
    log: document.getElementById('log-list'),
    hover: document.getElementById('hover-info'),
    banner: document.getElementById('banner'),
};

// ---- Coordinate helpers ----------------------------------------------------

function cellToScreen(cell) {
    // Diamond layout: each (x,y) becomes ((x+y)*w, (x-y)*h)
    const sx = (cell.x + cell.y) * cellSize.w + originX;
    const sy = (cell.x - cell.y) * cellSize.h + originY;
    return { sx, sy };
}

function screenToCell(mx, my) {
    // Inverse of cellToScreen, then look up the closest cell
    const dx = (mx - originX) / cellSize.w;
    const dy = (my - originY) / cellSize.h;
    const x = Math.round((dx + dy) / 2);
    const y = Math.round((dx - dy) / 2);
    // Find cell with these coords
    for (const c of state.cells) {
        if (c.x === x && c.y === y) return c;
    }
    return null;
}

function recomputeOrigin() {
    if (!state) return;
    let minSx = Infinity, maxSx = -Infinity, minSy = Infinity, maxSy = -Infinity;
    for (const c of state.cells) {
        const { sx, sy } = { sx: (c.x + c.y) * cellSize.w, sy: (c.x - c.y) * cellSize.h };
        if (sx < minSx) minSx = sx;
        if (sx > maxSx) maxSx = sx;
        if (sy < minSy) minSy = sy;
        if (sy > maxSy) maxSy = sy;
    }
    const fitW = (W - 40) / (maxSx - minSx + cellSize.w * 2);
    const fitH = (H - 40) / (maxSy - minSy + cellSize.h * 2);
    const fit = Math.min(fitW, fitH, 1);
    cellSize.w *= fit;
    cellSize.h *= fit;
    minSx *= fit; maxSx *= fit; minSy *= fit; maxSy *= fit;
    originX = (W - (maxSx + minSx)) / 2;
    originY = (H - (maxSy + minSy)) / 2;
}

// ---- Drawing ---------------------------------------------------------------

function drawDiamond(sx, sy, w, h, fill, stroke) {
    ctx.beginPath();
    ctx.moveTo(sx, sy - h);
    ctx.lineTo(sx + w, sy);
    ctx.lineTo(sx, sy + h);
    ctx.lineTo(sx - w, sy);
    ctx.closePath();
    if (fill) { ctx.fillStyle = fill; ctx.fill(); }
    if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = 1; ctx.stroke(); }
}

function draw() {
    ctx.fillStyle = '#0d1117';
    ctx.fillRect(0, 0, W, H);
    if (!state) return;

    const reachable = new Set(state.reachable_cells);
    const attackable = new Set(state.attackable_cells);
    const playerCellId = state.entities.find(e => e.is_player)?.cell;

    for (const c of state.cells) {
        const { sx, sy } = cellToScreen(c);
        let fill = '#1f2933';
        if (!c.walkable) fill = '#3a3a3a';
        else if (reachable.has(c.id)) fill = '#1d4d2c';
        if (attackable.has(c.id)) fill = '#5a1e1e';
        if (hoverCell && hoverCell.id === c.id) fill = '#3b82f6';
        drawDiamond(sx, sy, cellSize.w, cellSize.h, fill, '#0d1117');
    }

    // Draw entities
    for (const e of state.entities) {
        if (e.cell == null) continue;
        const cell = cellsById.get(e.cell);
        if (!cell) continue;
        const { sx, sy } = cellToScreen(cell);
        const r = Math.min(cellSize.w, cellSize.h * 2) * 0.7;
        ctx.beginPath();
        ctx.arc(sx, sy - r * 0.4, r, 0, Math.PI * 2);
        ctx.fillStyle = e.is_player ? '#58a6ff' : '#f85149';
        if (!e.alive) ctx.fillStyle = '#444';
        ctx.fill();
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 2;
        ctx.stroke();

        // HP text
        ctx.fillStyle = 'white';
        ctx.font = 'bold 11px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(e.hp, sx, sy - r * 0.4);

        // Name
        ctx.font = '10px sans-serif';
        ctx.fillStyle = e.is_player ? '#58a6ff' : '#f85149';
        ctx.fillText(e.name, sx, sy - r * 1.5);
    }
}

// ---- UI panels -------------------------------------------------------------

function fmtBar(klass, cur, max) {
    const pct = max > 0 ? (cur / max) * 100 : 0;
    return `<div class="bar ${klass}"><div style="width: ${pct}%"></div></div>
            <div class="bar-label"><span>${klass.toUpperCase()}</span><span>${cur} / ${max}</span></div>`;
}

function renderCards() {
    if (!state) { els.cards.innerHTML = ''; return; }
    els.cards.innerHTML = state.entities.map(e => `
        <div class="entity-card ${e.is_player ? 'is-player' : 'is-enemy'} ${e.alive ? '' : 'dead'}">
            <div class="name">
                <span>${e.name}</span>
                <span class="badge">${e.is_player ? 'YOU' : 'BOT'}</span>
            </div>
            ${fmtBar('hp', e.hp, e.max_hp)}
            ${fmtBar('tp', e.tp, e.max_tp)}
            ${fmtBar('mp', e.mp, e.max_mp)}
            <div class="stats">
                <span>STR</span><span>${e.strength}</span>
                <span>AGI</span><span>${e.agility}</span>
                <span>RES</span><span>${e.resistance}</span>
                <span>WIS</span><span>${e.wisdom}</span>
                <span>SCI</span><span>${e.science}</span>
                <span>MAG</span><span>${e.magic}</span>
            </div>
        </div>
    `).join('');
}

function renderWeapons() {
    if (!state) { els.weapons.innerHTML = ''; return; }
    const player = state.entities.find(e => e.is_player);
    if (!player) { els.weapons.innerHTML = ''; return; }
    const meta = new Map(state.weapons.map(w => [w.id, w]));
    const active = state.active_item || {};
    els.weapons.innerHTML = player.weapons.map(wid => {
        const w = meta.get(wid);
        const equipped = player.current_weapon === wid;
        const isActive = active.kind === 'weapon' && (active.id === wid || (active.id == null && equipped));
        return `<button class="item-btn ${equipped ? 'equipped' : ''} ${isActive ? 'active' : ''}" data-weapon-id="${wid}">
            ${w?.name ?? wid} ${equipped ? '✓' : ''}
            <small>range ${w?.min_range}-${w?.max_range}, cost ${w?.cost} TP</small>
        </button>`;
    }).join('');
    els.weapons.querySelectorAll('button').forEach(b => {
        b.addEventListener('click', () => setWeapon(parseInt(b.dataset.weaponId)));
    });
}

function renderChips() {
    if (!state) { els.chips.innerHTML = ''; return; }
    const player = state.entities.find(e => e.is_player);
    if (!player || !player.chips || player.chips.length === 0) {
        els.chips.innerHTML = '<div style="font-size:11px;color:#8b949e">No chips equipped.</div>';
        return;
    }
    const meta = new Map(state.chips.map(c => [c.id, c]));
    const active = state.active_item || {};
    els.chips.innerHTML = player.chips.map(cid => {
        const c = meta.get(cid);
        const cd = player.cooldowns?.[cid] || 0;
        const tooExpensive = player.tp < (c?.cost || 0);
        const disabled = cd > 0 || tooExpensive;
        const isActive = active.kind === 'chip' && active.id === cid;
        return `<button class="item-btn ${isActive ? 'active' : ''}" data-chip-id="${cid}" ${disabled ? 'disabled' : ''}>
            ${c?.name ?? cid}
            <small>range ${c?.min_range}-${c?.max_range}, cost ${c?.cost} TP${cd > 0 ? `, CD ${cd}` : ''}${c?.cooldown ? `, cd ${c.cooldown}` : ''}</small>
        </button>`;
    }).join('');
    els.chips.querySelectorAll('button').forEach(b => {
        b.addEventListener('click', () => selectChip(parseInt(b.dataset.chipId)));
    });
}

function renderLog() {
    if (!state || !state.log) return;
    for (const action of state.log) {
        const div = document.createElement('div');
        div.className = 'entry ' + classifyLog(action);
        div.textContent = formatLog(action);
        els.log.appendChild(div);
    }
    els.log.scrollTop = els.log.scrollHeight;
}

function classifyLog(a) {
    const t = a[0];
    if (t === 6) return 'turn';                 // NEW_TURN
    if (t === 7) return 'turn';                 // LEEK_TURN
    if (t === 101 || t === 109 || t === 110 || t === 111) return 'damage';
    if (t === 103 || t === 104 || t === 112) return 'heal';
    if (t === 10) return 'move';
    if (t === 13 || t === 16 || t === 12) return 'weapon';
    return '';
}

function formatLog(a) {
    const t = a[0];
    switch (t) {
        case 0: return '⚔ Fight starts';
        case 6: return `--- Turn ${a[1]} ---`;
        case 7: return `→ Entity #${a[1]} plays`;
        case 8: return `   end turn (${a[2]} TP, ${a[3]} MP left)`;
        case 10: return `   moves to cell ${a[2]} (${a[3]?.length ?? 0} cells)`;
        case 13: return `   equips weapon template ${a[1]}`;
        case 16: return `   shoots cell ${a[1]} (${a[2] === 1 ? 'hit' : a[2] === 2 ? 'CRIT' : 'miss'})`;
        case 101: return `   💢 entity #${a[1]} loses ${a[2]} HP (${a[3]} erosion)`;
        case 103: return `   ❤ entity #${a[1]} heals ${a[2]} HP`;
        case 5: return `   ☠ entity #${a[1]} dies`;
        case 4: return '🏁 Fight ends';
        case 203: return `   says: "${a[1]}"`;
        default: return JSON.stringify(a);
    }
}

function showBanner() {
    els.banner.classList.remove('show', 'win', 'lose', 'draw');
    if (!state || !state.finished) return;
    const player = state.entities.find(e => e.is_player);
    const playerTeam = player?.team;
    if (state.winner === playerTeam) {
        els.banner.textContent = '🏆 You win!';
        els.banner.classList.add('show', 'win');
    } else if (state.winner === -1) {
        els.banner.textContent = '🤝 Draw';
        els.banner.classList.add('show', 'draw');
    } else {
        els.banner.textContent = '☠ Defeat';
        els.banner.classList.add('show', 'lose');
    }
}

function updateActionPanel() {
    if (!state) return;
    if (state.finished) {
        els.status.textContent = 'Fight over.';
        els.endTurn.disabled = true;
        return;
    }
    if (state.is_player_turn) {
        els.status.textContent = 'Click a green cell to move, a red cell to shoot, or a weapon to equip it.';
        els.endTurn.disabled = false;
    } else {
        els.status.textContent = `Bot is thinking…`;
        els.endTurn.disabled = true;
    }
}

// ---- API calls -------------------------------------------------------------

async function api(path, body) {
    const r = await fetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body || {}),
    });
    return r.json();
}

async function newGame(seed) {
    const data = await api('/api/new_game', seed != null ? { seed } : {});
    setState(data);
}

async function setWeapon(weaponId) {
    if (!state || !state.is_player_turn) return;
    const data = await api('/api/set_weapon', { weapon_id: weaponId });
    setState(data.state);
}

async function moveTo(cellId) {
    if (!state || !state.is_player_turn) return;
    const data = await api('/api/move', { cell_id: cellId });
    setState(data.state);
}

async function useWeapon(cellId) {
    if (!state || !state.is_player_turn) return;
    const data = await api('/api/use_weapon', { cell_id: cellId });
    setState(data.state);
}

async function useChip(chipId, cellId) {
    if (!state || !state.is_player_turn) return;
    const data = await api('/api/use_chip', { chip_id: chipId, cell_id: cellId });
    setState(data.state);
}

async function selectChip(chipId) {
    if (!state || !state.is_player_turn) return;
    const data = await api('/api/select_item', { kind: 'chip', item_id: chipId });
    setState(data);
}

async function endTurn() {
    if (!state || !state.is_player_turn) return;
    els.status.textContent = 'Bot is thinking…';
    els.endTurn.disabled = true;
    // Small delay so the UI updates before the (potentially synchronous) bot turn
    await new Promise(r => setTimeout(r, 50));
    const data = await api('/api/end_turn');
    setState(data);
}

// ---- State management ------------------------------------------------------

function setState(newState) {
    // Append new log entries before replacing
    if (state && newState.log) {
        const carry = state.log || [];
        // newState.log already only contains the delta from the controller
    }
    state = newState;
    cellsById = new Map(state.cells.map(c => [c.id, c]));
    els.seed.textContent = `seed ${state.seed}`;
    recomputeOrigin();
    renderCards();
    renderWeapons();
    renderChips();
    updateActionPanel();
    renderLog();
    showBanner();
    draw();
}

// ---- Mouse interaction -----------------------------------------------------

canvas.addEventListener('mousemove', (ev) => {
    const rect = canvas.getBoundingClientRect();
    const mx = ev.clientX - rect.left;
    const my = ev.clientY - rect.top;
    hoverCell = state ? screenToCell(mx, my) : null;
    if (hoverCell) {
        els.hover.textContent = `cell ${hoverCell.id}  (x=${hoverCell.x}, y=${hoverCell.y})`;
    } else {
        els.hover.textContent = '';
    }
    draw();
});

canvas.addEventListener('click', (ev) => {
    if (!state || !state.is_player_turn || state.finished) return;
    const rect = canvas.getBoundingClientRect();
    const cell = screenToCell(ev.clientX - rect.left, ev.clientY - rect.top);
    if (!cell) return;
    if (state.attackable_cells.includes(cell.id)) {
        const active = state.active_item || {};
        if (active.kind === 'chip' && active.id != null) {
            useChip(active.id, cell.id);
        } else {
            useWeapon(cell.id);
        }
    } else if (state.reachable_cells.includes(cell.id)) {
        moveTo(cell.id);
    }
});

els.newGame.addEventListener('click', () => {
    els.log.innerHTML = '';
    newGame();
});
els.endTurn.addEventListener('click', endTurn);

// Boot
newGame();
