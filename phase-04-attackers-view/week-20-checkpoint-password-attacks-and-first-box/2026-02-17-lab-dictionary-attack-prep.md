---
title: "Dictionary Attack Prep: Login Responses and Wordlists"
date: 2026-02-17
type: lab
phase: 4
week: 20
source: LabEx guided lab
category: Authentication
attack: [T1110.001]
tools: [head, web browser]
tags: [brute-force, dictionary-attack, authentication, wordlists, user-enumeration]
status: Part 1 of 2 (Hydra automation to follow)
---

# Dictionary Attack Prep: Login Responses and Wordlists

> **Scope:** Performed inside a LabEx guided lab environment built for this exercise. No real systems were targeted.

## TL;DR
- I probed a lab login page by hand and confirmed it returns one generic error (`Invalid Username or Password!`) for every failed attempt, so it doesn't leak which usernames exist.
- I inspected `500-worst-passwords.txt`, the kind of wordlist attackers feed into tools like Hydra for dictionary attacks.
- **ATT&CK:** T1110.001 (Brute Force: Password Guessing).
- **Defender takeaway:** a burst of failed logins from one source against one endpoint is the signal to watch for. There's a draft detection rule below.
- **Next:** part 2 automates the attack with Hydra against the same login page.

---

## Objective
Understand how a web login responds to failed authentication, and how a pre-compiled password list makes brute-forcing practical. This is the reconnaissance-and-preparation stage before automating the attack with Hydra.

## What I did
1. **Manual login attempts:** submitted several incorrect username/password combinations to the lab's authentication page and recorded each response.
2. **Obtained a wordlist:** `/home/labex/project/500-worst-passwords.txt`, a list of the most commonly used weak passwords.
3. **Inspected the wordlist:** read the first 10 entries to see what an attacker would try first:
   ```bash
   head -n 10 500-worst-passwords.txt
   ```

## What I found
- **No username enumeration:** every failed attempt returned the same message, `Invalid Username or Password!`, whether or not the username existed. An attacker can't use the error text to build a list of valid accounts first, so they must guess username *and* password together, which multiplies the work.
- **Weak passwords are predictable:** the wordlist's top entries are the kind of short, common passwords that millions of people still use. A dictionary attack tries these first, which is far more efficient than trying every possible combination.
- **Manual guessing is the same attack, just slow:** my hand-typed attempts were a basic brute-force attack. Tools like Hydra run the same loop across thousands of candidates per minute.

## How I found it
**Login behaviour:** I compared the page's responses across several wrong inputs. The message never changed.

![Generic error message returned for incorrect credentials](https://github.com/user-attachments/assets/d89c03cc-042d-4fb6-a994-9e5178f7ae51)

**Wordlist contents:** I read the top of the file with `head`.

![First 10 lines of 500-worst-passwords.txt](https://github.com/user-attachments/assets/3e87cb6b-34bf-4723-827e-c2bd7230340a)

---

## Key concepts
| Term | What it means |
|---|---|
| **Brute-force attack** | Systematically trying many credentials until one works. |
| **Dictionary attack** | A brute-force attack that uses a list of likely passwords (a *wordlist*) instead of every possible combination. |
| **Wordlist** | A text file of candidate passwords, usually ordered by how common they are (e.g. `500-worst-passwords.txt`, `rockyou.txt`). |
| **User enumeration** | Working out which usernames exist from differences in a system's responses (error text, response time, status code). Generic errors defeat the text-based version. |
| **Online vs offline attack** | *Online:* guessing against a live login (throttling and lockouts apply). *Offline:* cracking stolen password hashes locally at full hardware speed. This lab is online. |

## MITRE ATT&CK mapping
| Tactic | Technique | How it applies here |
|---|---|---|
| Credential Access | [T1110.001 Brute Force: Password Guessing](https://attack.mitre.org/techniques/T1110/001/) | Guessing passwords against a live login page, first by hand, next with a wordlist. |

## Detection: the defender's view
**What it looks like in the logs:** many failed login requests (`POST` to the login endpoint) from a single source IP in a short window, often cycling through usernames or passwords in wordlist order, and often with a non-browser User-Agent once a tool like Hydra is used.

**Log sources:** web server access logs, application authentication logs, WAF logs.

**Draft Sigma rule** *(untested draft, not yet validated against real logs):*
```yaml
title: Possible Web Login Brute Force (Many Failed Logins From One Source)
name: possible_web_login_brute_force
status: experimental
description: Detects a burst of POST requests to a login endpoint from a single IP, typical of dictionary attacks such as Hydra.
logsource:
  category: webserver
detection:
  selection:
    cs-method: 'POST'
    cs-uri-stem|contains: 'login'
  condition: selection
fields: [c-ip, cs-uri-stem, cs-user-agent]
level: medium
---
title: Web Login Brute Force Threshold
correlation:
  type: event_count
  rules:
    - possible_web_login_brute_force
  group-by:
    - c-ip
  timespan: 5m
  condition:
    gte: 20
level: high
```
*Tuning notes:* the threshold of 20 in 5 minutes is a starting guess. Pages that return HTTP 200 on failure (like this one) need the application's auth log or the response body to tell failure from success.

## Fix/remediation
- **Keep generic error messages.** This page already does it right.
- **Throttle and lock out:** limit failed attempts per account and per source IP. The UK's Cyber Essentials scheme expects brute-force protection, such as locking or throttling after no more than 10 unsuccessful attempts.
- **Block common passwords:** check new passwords against a deny-list of known weak ones. The UK NCSC recommends this over forcing complexity rules.
- **Multi-factor authentication:** a guessed password alone is then no longer enough.
- **Monitor and alert** on failed-login bursts (see the detection above).

## Lessons learned
- At first I thought of the generic error as "security through obscurity". It's better described as **preventing user enumeration**, a deliberate, recognised control, not just hiding things.
- Password *requirements* matter, but length and blocking common passwords beat complexity rules. A "complex" password like `Password1!` still sits near the top of real wordlists.
- Seeing a real wordlist made it obvious why weak passwords fall first: attackers don't need to be clever, just ordered.

## Next steps
- **Part 2:** run Hydra against the same lab login with this wordlist, then study what the attack looks like from the server's logs and test the draft detection rule above.

## Tools used
- LabEx guided lab environment
- Web browser (manual login attempts)
- `head` (Linux)
