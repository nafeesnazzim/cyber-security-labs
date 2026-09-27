# Cybersecurity Labs

Hands-on practice environment I built and maintain alongside my BSc (Hons) Cyber Security at the University of Staffordshire (APIIT, Colombo).

## What's here
| Folder | Contents |
|---|---|
| `lab-setup/` | How my isolated VirtualBox lab is built (Kali Linux + Windows on a host-only network) |
| `port-scanner/` | A Python TCP port scanner using the `socket` module, tested against my own lab hosts |
| `ROADMAP.md` | My self-designed cloud security learning roadmap and progress |
| `writeups/` | Lab write-ups, grouped by category (index below) |

## Writeups
| Date | Writeup | Category | ATT&CK | Tools |
|---|---|---|---|---|
| 2026-02-17 | [Dictionary Attack Prep: Login Responses and Wordlists](writeups/authentication/2026-02-17-dictionary-attack-prep.md) | Authentication | [T1110.001](https://attack.mitre.org/techniques/T1110/001/) | head, web browser |

## Tools practised in the lab
Wireshark (packet analysis) · Nmap and OpenVAS (vulnerability scanning) · Metasploit · Linux (Debian, Kali) and Windows administration · Python and Bash

## Ethics
Everything here is used only against machines I own inside an isolated host-only network. Do not scan or test systems you do not have permission to test.
