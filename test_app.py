import subprocess
import unittest
from unittest.mock import patch

import app


class PingSummaryTests(unittest.TestCase):
    def test_summarizes_successful_ping_output(self):
        output = (
            "4 packets transmitted, 4 received, 0% packet loss, time 3004ms\n"
            "rtt min/avg/max/mdev = 0.021/0.035/0.049/0.010 ms\n"
        )
        self.assertEqual(
            app.summarize_ping(output, 0),
            {"success": True, "rtt_avg_ms": 0.035, "loss_percent": 0.0},
        )

    def test_summarizes_partial_loss_as_success_if_host_replied(self):
        output = "4 packets transmitted, 1 received, 75% packet loss, time 3002ms\n"
        self.assertEqual(
            app.summarize_ping(output, 1),
            {"success": True, "rtt_avg_ms": None, "loss_percent": 75.0},
        )

    def test_summarizes_no_response(self):
        output = "4 packets transmitted, 0 received, 100% packet loss, time 3004ms\n"
        self.assertEqual(
            app.summarize_ping(output, 1),
            {"success": False, "rtt_avg_ms": None, "loss_percent": 100.0},
        )


class PingApiTests(unittest.TestCase):
    def setUp(self):
        app.app.config["TESTING"] = True
        self.client = app.app.test_client()

    @patch("app.run_ping")
    def test_pings_ip_and_returns_metrics(self, mock_run_ping):
        mock_run_ping.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=(
                "2 packets transmitted, 2 received, 0% packet loss, time 1001ms\n"
                "rtt min/avg/max/mdev = 0.030/0.040/0.050/0.010 ms\n"
            ),
            stderr="",
        )

        response = self.client.post(
            "/api/ping", json={"host": "127.0.0.1", "count": 2}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                "host": "127.0.0.1",
                "count": 2,
                "success": True,
                "rtt_avg_ms": 0.04,
                "loss_percent": 0.0,
            },
        )
        mock_run_ping.assert_called_once_with("127.0.0.1", count=2)

    def test_rejects_invalid_ip(self):
        response = self.client.post(
            "/api/ping", json={"host": "localhost", "count": 1}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("有效的 IPv4 或 IPv6", response.get_json()["error"])

    def test_rejects_invalid_ping_count(self):
        for count in [0, 21, True, "2"]:
            with self.subTest(count=count):
                response = self.client.post(
                    "/api/ping", json={"host": "127.0.0.1", "count": count}
                )
                self.assertEqual(response.status_code, 400)

    def test_serves_web_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("開始 Ping".encode(), response.data)


if __name__ == "__main__":
    unittest.main()
