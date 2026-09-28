# Cybersecurity Labs: My Self Study Journey

Hands-on practice and learning notes I build and maintain alongside my BSc (Hons) Cyber Security at the University of Staffordshire (APIIT, Colombo).

I'm working through a self-designed **71-week roadmap**, from foundations and networking through operating systems, scripting, offensive and defensive fundamentals, to AWS cloud security and threat hunting. Every week gets documented here as it happens:

- 📘 **Learning notes:** the concepts I studied, explained in my own words
- 🧪 **Labs:** what I did, what I found and how, with screenshots; from Phase 6 onwards also MITRE ATT&CK mapping and a defender's detection view

## Progress

<!-- PROGRESS:START -->
![Roadmap progress](https://img.shields.io/badge/roadmap-0%2F71%20weeks%20%280%25%29-2ea44f) ![In progress](https://img.shields.io/badge/in%20progress-3%20weeks-dbab09)

**3 entries** across the roadmap. ✅ complete (notes + hands-on) · 🟡 started · ⬜ not started

| Phase | Weeks | Progress | Entries |
|---|---|---|---|
| [1. Foundations & Security Mindset](phase-01-foundations/) | 1–4 | ⬜⬜⬜⬜ 0/4 | 0 |
| [2. Networking](phase-02-networking/) | 5–10 | ⬜⬜⬜⬜⬜⬜ 0/6 | 0 |
| [3. Operating Systems (Linux + Windows) & Homelab Build](phase-03-operating-systems/) | 11–23 | ⬜⬜⬜⬜🟡⬜ 0/13 | 1 |
| [4. Scripting & Programming for Security](phase-04-scripting/) | 24–29 | ⬜⬜⬜⬜⬜🟡 0/6 | 1 |
| [5. Core Security Concepts](phase-05-core-security-concepts/) | 30–35 | ⬜⬜⬜⬜⬜⬜ 0/6 | 0 |
| [6. Offensive Fundamentals](phase-06-offensive-fundamentals/) | 36–43 | ⬜⬜⬜⬜⬜⬜🟡⬜ 0/8 | 1 |
| [7. Defensive Fundamentals](phase-07-defensive-fundamentals/) | 44–51 | ⬜⬜⬜⬜⬜⬜⬜⬜ 0/8 | 0 |
| [8. Specialisation Branch](phase-08-specialisation-branch/) | 52–61 | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0/10 | 0 |
| [9. Advanced Topics & Career Prep](phase-09-advanced-topics/) | 62–71 | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0/10 | 0 |

### Latest entries

| Date | Entry | Type | Week | ATT&CK |
|---|---|---|---|---|
| 2026-09-26 | [Homelab Build: Isolated VirtualBox Lab](phase-03-operating-systems/week-22-homelab-build/2026-09-26-lab-homelab-build.md) | Lab | Week 22 | — |
| 2026-09-26 | [Python TCP Port Scanner](phase-04-scripting/week-29-checkpoint-build-a-small-end-to-end-tool/2026-09-26-lab-python-port-scanner.md) | Lab | Week 29 | — |
| 2026-02-17 | [Dictionary Attack Prep: Login Responses and Wordlists](phase-06-offensive-fundamentals/week-42-password-attacks/2026-02-17-lab-dictionary-attack-prep.md) | Lab | Week 42 | [T1110.001](https://attack.mitre.org/techniques/T1110/001/) |

Full history: [CHANGELOG.md](CHANGELOG.md)
<!-- PROGRESS:END -->

## How this repo is organised
```
phase-02-networking/
  README.md                          ← phase overview, cert alignment, week-by-week status
  week-06-ip-addressing-and-subnetting/
    YYYY-MM-DD-learn-<topic>.md      ← learning notes
    YYYY-MM-DD-lab-<topic>.md        ← hands-on lab
```
A week is marked ✅ once it has both learning notes and a hands-on lab. Checkpoint weeks (🔄) consolidate each phase.

## Extra practice (outside the roadmap)
Boot2root VMs and other practice done for its own sake, not tied to a roadmap phase/week:
- [EH Practical Exam Prep](extra-practice/eh-exam-prep/): VulnHub's DC series, for my Ethical Hacking module's practical exam

## Tools practised in the lab
Wireshark (packet analysis) · Nmap and OpenVAS (vulnerability scanning) · Metasploit · Linux (Debian, Kali) and Windows administration · Python and Bash

## Ethics
Everything here is done only against machines I own inside an isolated host-only network, or on platforms built for practice. Do not scan or test systems you do not have permission to test.
