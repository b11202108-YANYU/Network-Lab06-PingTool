"""A small command-line wrapper around the system ping utility."""

import argparse
import subprocess
import sys
from typing import Sequence


def positive_integer(value: str) -> int:
    """Parse a positive integer for CLI options."""
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer") from error
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def run_ping(host: str, count: int = 4, timeout: int = 1) -> subprocess.CompletedProcess[str]:
    """Run the system ping command and return its result."""
    if not host.strip():
        raise ValueError("host must not be empty")
    if count <= 0:
        raise ValueError("count must be greater than zero")
    if timeout <= 0:
        raise ValueError("timeout must be greater than zero")

    return subprocess.run(
        ["ping", "-c", str(count), "-W", str(timeout), "--", host],
        capture_output=True,
        text=True,
        check=False,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Send ICMP echo requests to a host using the system ping utility."
    )
    parser.add_argument("host", help="hostname or IP address to ping")
    parser.add_argument(
        "-c", "--count", type=positive_integer, default=4, help="number of requests (default: 4)"
    )
    parser.add_argument(
        "-W",
        "--timeout",
        type=positive_integer,
        default=1,
        help="wait seconds for each response (default: 1)",
    )
    args = parser.parse_args(argv)

    try:
        result = run_ping(args.host, args.count, args.timeout)
    except FileNotFoundError:
        print("Error: system 'ping' command was not found.", file=sys.stderr)
        return 127
    except ValueError as error:
        parser.error(str(error))

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
