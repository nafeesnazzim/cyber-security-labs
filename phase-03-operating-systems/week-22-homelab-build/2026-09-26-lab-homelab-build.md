---
title: "Homelab Build: Isolated VirtualBox Lab"
date: 2026-09-26
type: lab
phase: 3
week: 22
source: Homelab
tools: [VirtualBox, Kali Linux, Windows, Wireshark, Nmap, OpenVAS, Metasploit]
tags: [homelab, virtualbox, network-isolation, lab-safety]
---

# Homelab Build: Isolated VirtualBox Lab

## Purpose
An isolated VirtualBox environment for practising packet analysis, vulnerability scanning, exploitation and systems administration without touching my home network or the internet.

## Network design
- Every VM uses a single VirtualBox **host-only adapter** on `192.168.56.0/24`.
- No NAT or bridged adapter is attached while testing.
- A host-only network connects only the VMs and the host machine, so scans and exploits cannot reach my home network or the internet.

## Virtual machines
All software is kept on its latest release (VirtualBox, Kali Linux, Windows).

| VM | Role | RAM |
|---|---|---|
| Kali Linux | Attacker: scanning, exploitation, packet capture | 4 GB |
| Windows | Target and Windows administration practice | 2 GB |

## Snapshots
I take a clean snapshot of each VM before every exercise and roll back to it afterwards, so each exercise starts from a known state.

## Tools installed
- Wireshark: packet capture and analysis
- Nmap: host discovery and port scanning
- OpenVAS: vulnerability scanning
- Metasploit: exploitation practice against my own targets

## Safety rules
1. Only test machines I own inside this host-only network.
2. Never point tools at public IP addresses or anyone else's systems.
3. No NAT or bridged adapter while an exercise is running.
4. Roll back to a clean snapshot after each exercise.
