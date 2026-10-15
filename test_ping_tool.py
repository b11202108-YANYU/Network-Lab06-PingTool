import argparse
import io
import subprocess
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

import ping_tool


class PositiveIntegerTests(unittest.TestCase):
    def test_accepts_positive_integer(self):
        self.assertEqual(ping_tool.positive_integer("3"), 3)

    def test_rejects_zero(self):
        with self.assertRaisesRegex(argparse.ArgumentTypeError, "greater than zero"):
            ping_tool.positive_integer("0")

    def test_rejects_non_integer(self):
        with self.assertRaisesRegex(argparse.ArgumentTypeError, "must be an integer"):
            ping_tool.positive_integer("abc")


class RunPingTests(unittest.TestCase):
    @patch("ping_tool.subprocess.run")
    def test_builds_command_and_returns_result(self, mock_run):
        expected = subprocess.CompletedProcess(args=[], returncode=0, stdout="ok\n", stderr="")
        mock_run.return_value = expected

        result = ping_tool.run_ping("example.com", count=2, timeout=3)

        self.assertIs(result, expected)
        mock_run.assert_called_once_with(
            ["ping", "-c", "2", "-W", "3", "--", "example.com"],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_rejects_invalid_arguments(self):
        for args in [
            (" ", 1, 1),
            ("example.com", 0, 1),
            ("example.com", 1, 0),
        ]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                ping_tool.run_ping(*args)

    @patch("ping_tool.run_ping")
    def test_main_prints_output_and_returns_ping_status(self, mock_ping):
        mock_ping.return_value = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="ping output\n", stderr="ping error\n"
        )
        stdout = io.StringIO()
        stderr = io.StringIO()

        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = ping_tool.main(["-c", "2", "bad.example"])

        self.assertEqual(status, 1)
        self.assertEqual(stdout.getvalue(), "ping output\n")
        self.assertEqual(stderr.getvalue(), "ping error\n")
        mock_ping.assert_called_once_with("bad.example", 2, 1)


if __name__ == "__main__":
    unittest.main()
