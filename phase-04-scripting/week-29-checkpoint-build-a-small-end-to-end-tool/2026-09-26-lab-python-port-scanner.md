---
title: "Python TCP Port Scanner"
date: 2026-09-26
type: lab
phase: 4
week: 29
source: Homelab
tools: [Python, socket]
tags: [python, port-scanning, networking, tooling]
---

# Python TCP Port Scanner

Source code: [`port-scanner/port_scanner.py`](port-scanner/port_scanner.py)

A Python TCP connect scanner built with the `socket` module and tested against hosts in my isolated home lab (see [homelab build](../../phase-03-operating-systems/week-22-homelab-build/2026-09-26-lab-homelab-build.md)).

## What it does
For each port in the chosen range, the scanner attempts a full TCP connection with `connect_ex`. If the connection succeeds, the port is reported as open, together with its usual service name. Ports are scanned in parallel threads to keep scans fast.

## Usage
```bash
# Scan the first 1024 ports of a lab VM
python3 port-scanner/port_scanner.py 192.168.56.101

# Scan specific ports
python3 port-scanner/port_scanner.py 192.168.56.101 -p 22,80,443

# Full range with a longer timeout and fewer parallel connections
python3 port-scanner/port_scanner.py 192.168.56.101 -p 1-65535 -t 1 -w 50
```

| Option | Meaning | Default |
|---|---|---|
| `-p` | Ports: a list (`22,80,443`), a range (`1-1024`) or both | `1-1024` |
| `-t` | Timeout per port, in seconds | `0.5` |
| `-w` | Parallel connections | `100` |

## Output format
```
Scanning <target> (<number of ports> ports)...
  <port>/tcp open  <service>
Done: <count> open port(s) found.
```

## Ethics
Lab use only. Run it only against machines you own or are explicitly authorised to test.

## What I learned
Building and testing this scanner strengthened my scripting skills and my understanding of how TCP connections, ports and services work at the socket level.
