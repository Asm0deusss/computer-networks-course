import argparse
import re
import subprocess

HEADERS_SIZE = 28


def is_valid_hostname(hostname):
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1] # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def ping(host: str, mtu: int) -> subprocess.CompletedProcess:

    command: list = ["ping", host, "-M", "do", "-s", str(mtu), "-c", "3"]
    runner = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    return runner


def find_mtu(host: str) -> int:
    left_border, right_border = 0, 9001 - HEADERS_SIZE

    while left_border + 1 < right_border:
        middle_value = (left_border + right_border) // 2

        ping_result: subprocess.CompletedProcess = ping(host, middle_value)

        ping_code, out_stream, err_stream = (
            ping_result.returncode,
            ping_result.stdout,
            ping_result.stderr,
        )

        if ping_code == 0:
            left_border = middle_value

        elif ping_code == 1:
            right_border = middle_value

        else:
            exit(err_stream)

    return left_border + HEADERS_SIZE


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host")

    args = parser.parse_args()

    host: str = args.host
    if not is_valid_hostname(host):
        print("Invalid host. Stopping...")
        exit(1)

    icmp_enabled = subprocess.run(
        ["cat", "/proc/sys/net/ipv4/icmp_echo_ignore_all"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )

    if icmp_enabled.stdout == 1:
        print("ISCMP is disabled. Stopping...")
        exit(1)

    print("Starting MTU search")
    result = find_mtu(host)

    print(f"Found MTU = {result}")


main()
