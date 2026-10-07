# Cyber Security Labs: My Self Study Journey

Hands-on practice and learning notes I build and maintain alongside my BSc (Hons) Cyber Security at the University of Staffordshire (APIIT, Colombo).

I'm working through a self-designed **38-week roadmap** aimed squarely at **cloud security and threat hunting**: foundations and Linux, scripting (including AWS audit scripts in boto3), AWS core and secure configuration, a light look at the attacker's view, then detection and threat hunting on AWS — CloudTrail, GuardDuty, Athena and MITRE ATT&CK. Every week gets documented here as it happens:

- 📘 **Learning notes:** the concepts I studied, explained in my own words
- 🧪 **Labs:** what I did, what I found and how, with screenshots; on attack-relevant and detection labs, also a MITRE ATT&CK mapping and a defender's detection view

## Progress

<!-- PROGRESS:START -->
![Roadmap progress](https://img.shields.io/badge/roadmap-0%2F38%20weeks%20%280%25%29-2ea44f) ![In progress](https://img.shields.io/badge/in%20progress-3%20weeks-dbab09)

**3 entries** across the roadmap. ✅ complete (notes + hands-on) · 🟡 started · ⬜ not started

| Phase | Weeks | Progress | Entries |
|---|---|---|---|
| [1. Foundations & the Defender's Baseline](phase-01-foundations/) | 1–6 | ⬜⬜⬜🟡⬜⬜ 0/6 | 1 |
| [2. Scripting for Cloud Security](phase-02-scripting/) | 7–11 | 🟡⬜⬜⬜⬜ 0/5 | 1 |
| [3. AWS Core & Secure Configuration](phase-03-aws-core/) | 12–17 | ⬜⬜⬜⬜⬜⬜ 0/6 | 0 |
| [4. The Attacker's View (light)](phase-04-attackers-view/) | 18–20 | ⬜⬜🟡 0/3 | 1 |
| [5. Windows, AD & Logs](phase-05-windows-ad-logs/) | 21–23 | ⬜⬜⬜ 0/3 | 0 |
| [6. Detection & Threat Hunting](phase-06-detection-hunting/) | 24–32 | ⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0/9 | 0 |
| [7. Breadth & Career](phase-07-breadth-career/) | 33–38 | ⬜⬜⬜⬜⬜⬜ 0/6 | 0 |

### Latest entries

| Date | Entry | Type | Week | ATT&CK |
|---|---|---|---|---|
| 2026-09-26 | [Homelab Build: Isolated VirtualBox Lab](phase-01-foundations/week-04-linux-command-line-part-1/2026-09-26-lab-homelab-build.md) | Lab | Week 4 | — |
| 2026-09-26 | [Python TCP Port Scanner](phase-02-scripting/week-07-python-refreshed-security-flavoured/2026-09-26-lab-python-port-scanner.md) | Lab | Week 7 | — |
| 2026-02-17 | [Dictionary Attack Prep: Login Responses and Wordlists](phase-04-attackers-view/week-20-checkpoint-password-attacks-and-first-box/2026-02-17-lab-dictionary-attack-prep.md) | Lab | Week 20 | [T1110.001](https://attack.mitre.org/techniques/T1110/001/) |

Full history: [CHANGELOG.md](CHANGELOG.md)
<!-- PROGRESS:END -->

## How this repo is organised
```
phase-06-detection-hunting/
  README.md                          ← phase overview, cert alignment, week-by-week status
  week-26-cloudtrail-deep-dive/
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
