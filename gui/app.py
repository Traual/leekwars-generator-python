"""Flask backend serving the leekwars Python generator GUI.

Run with:
    cd leekwars_generator_python
    python -m gui.app
Then open http://127.0.0.1:5000 in your browser.
"""

import os
import random
import sys

# Make the parent leekwars/ importable when ``python -m gui.app`` is run
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, render_template, request

from leekwars.generator import Generator
from gui.controller import FightController


HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "data")

app = Flask(__name__,
            template_folder=os.path.join(HERE, "templates"),
            static_folder=os.path.join(HERE, "static"))

# Singleton generator (loads weapons/chips/summons/components once)
_generator = Generator(data_dir=DATA_DIR)
# Single fight at a time (single-user app)
_state = {"controller": None}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/new_game", methods=["POST"])
def new_game():
    data = request.get_json(silent=True) or {}
    seed = int(data.get("seed") or random.randint(1, 2**30))
    _state["controller"] = FightController(_generator, seed)
    return jsonify(_state["controller"].get_state_dict())


@app.route("/api/state", methods=["GET"])
def state():
    if _state["controller"] is None:
        return jsonify({"error": "no game in progress"}), 400
    return jsonify(_state["controller"].get_state_dict())


@app.route("/api/set_weapon", methods=["POST"])
def set_weapon():
    if _state["controller"] is None:
        return jsonify({"error": "no game"}), 400
    data = request.get_json() or {}
    ok = _state["controller"].player_set_weapon(int(data["weapon_id"]))
    return jsonify({"ok": ok, "state": _state["controller"].get_state_dict()})


@app.route("/api/move", methods=["POST"])
def move():
    if _state["controller"] is None:
        return jsonify({"error": "no game"}), 400
    data = request.get_json() or {}
    used = _state["controller"].player_move_to(int(data["cell_id"]))
    return jsonify({"used_mp": used, "state": _state["controller"].get_state_dict()})


@app.route("/api/use_weapon", methods=["POST"])
def use_weapon():
    if _state["controller"] is None:
        return jsonify({"error": "no game"}), 400
    data = request.get_json() or {}
    result = _state["controller"].player_use_weapon(int(data["cell_id"]))
    return jsonify({"result": result, "state": _state["controller"].get_state_dict()})


@app.route("/api/end_turn", methods=["POST"])
def end_turn():
    if _state["controller"] is None:
        return jsonify({"error": "no game"}), 400
    _state["controller"].end_player_turn()
    return jsonify(_state["controller"].get_state_dict())


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
