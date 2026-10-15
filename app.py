from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from database import get_recent_events, get_tracks, init_db, trigger_effect

app = Flask(__name__)


@app.before_request
def setup() -> None:
    init_db()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/tracks")
def api_tracks():
    return jsonify(get_tracks())


@app.get("/api/events")
def api_events():
    return jsonify(get_recent_events())


@app.post("/api/effects")
def api_effects():
    payload = request.get_json(silent=True) or {}
    effect = payload.get("effect", "laser_smoke")
    result = trigger_effect(effect)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
