#!/usr/bin/env python3
"""Simple TCP connect port scanner for my isolated home lab.

Use only against hosts you own or are explicitly authorised to test.
"""
import argparse
import socket
from concurrent.futures import ThreadPoolExecutor


def parse_ports(spec: str) -> list[int]:
    """Parse '22,80,443' or '1-1024' (or a mix) into a sorted list of ports."""
    ports = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            start, end = (int(p) for p in part.split("-", 1))
            ports.update(range(start, end + 1))
        elif part:
            ports.add(int(part))
    return sorted(p for p in ports if 1 <= p <= 65535)


def scan_port(host: str, port: int, timeout: float) -> int | None:
    """Return the port if a TCP connection succeeds, otherwise None."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        return port if sock.connect_ex((host, port)) == 0 else None


def main() -> None:
    parser = argparse.ArgumentParser(description="TCP connect port scanner (lab use only)")
    parser.add_argument("host", help="target IP or hostname inside your lab")
    parser.add_argument("-p", "--ports", default="1-1024", help="e.g. 22,80,443 or 1-1024")
    parser.add_argument("-t", "--timeout", type=float, default=0.5, help="seconds per port")
    parser.add_argument("-w", "--workers", type=int, default=100, help="parallel connections")
    args = parser.parse_args()

    target = socket.gethostbyname(args.host)
    ports = parse_ports(args.ports)
    print(f"Scanning {target} ({len(ports)} ports)...")

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = pool.map(lambda p: scan_port(target, p, args.timeout), ports)

    open_ports = [p for p in results if p]
    for port in open_ports:
        try:
            service = socket.getservbyport(port, "tcp")
        except OSError:
            service = "unknown"
        print(f"  {port}/tcp open  {service}")
    print(f"Done: {len(open_ports)} open port(s) found.")


if __name__ == "__main__":
    main()
