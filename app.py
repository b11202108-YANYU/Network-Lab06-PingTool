"""Flask web interface for the system ping utility."""

import ipaddress
import re
import subprocess

from flask import Flask, jsonify, render_template, request

from ping_tool import run_ping

app = Flask(__name__)

MAX_COUNT = 20
LOSS_PATTERN = re.compile(r"([\d.]+)% packet loss")
RECEIVED_PATTERN = re.compile(r"\d+ packets transmitted,\s*(\d+)(?: packets?)? received")
RTT_PATTERN = re.compile(r"=\s*([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)\s*ms")


def summarize_ping(output: str, returncode: int) -> dict[str, int | float | bool | None]:
    """Extract packet loss and average round-trip time from iputils output."""
    loss_match = LOSS_PATTERN.search(output)
    received_match = RECEIVED_PATTERN.search(output)
    rtt_match = RTT_PATTERN.search(output)

    loss_percent = float(loss_match.group(1)) if loss_match else None
    received = int(received_match.group(1)) if received_match else 0
    rtt_avg_ms = float(rtt_match.group(2)) if rtt_match else None

    return {
        "success": received > 0 if received_match else returncode == 0,
        "rtt_avg_ms": rtt_avg_ms,
        "loss_percent": loss_percent,
    }


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/ping")
def ping():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="請提供 JSON 格式的目標 IP 與 Ping 次數。"), 400

    host = payload.get("host")
    count = payload.get("count", 4)
    if not isinstance(host, str) or not host.strip():
        return jsonify(error="請輸入有效的 IP 位址。"), 400
    try:
        ipaddress.ip_address(host.strip())
    except ValueError:
        return jsonify(error="目標必須是有效的 IPv4 或 IPv6 位址。"), 400

    if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= MAX_COUNT:
        return jsonify(error=f"Ping 次數必須是 1 到 {MAX_COUNT} 之間的整數。"), 400

    try:
        result = run_ping(host.strip(), count=count)
    except FileNotFoundError:
        app.logger.exception("System ping command was not found")
        return jsonify(error="找不到系統 ping 指令。"), 500
    except OSError:
        app.logger.exception("Could not execute system ping command")
        return jsonify(error="無法執行系統 ping 指令。"), 500

    summary = summarize_ping(result.stdout + result.stderr, result.returncode)
    return jsonify(host=host.strip(), count=count, **summary)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
