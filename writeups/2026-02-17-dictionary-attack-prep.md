---
title: "Dictionary Attack Prep: Login Responses and Wordlists"
date: 2026-02-17
platform: LabEx (guided lab)
category: Authentication / password attacks
tools: [head]
tags: [brute-force, dictionary-attack, authentication, wordlists]
status: In progress (Hydra stage not yet completed)
---

# Dictionary Attack Prep: Login Responses and Wordlists

## Objective
Understand how a login page responds to failed authentication attempts, and how a pre-compiled password list is used to automate a brute-force attack. This is the groundwork for a later Hydra exercise in the same LabEx lab.

## What I did
1. Made several manual login attempts with incorrect credentials against the lab's authentication page and observed the response.
2. Obtained a list of common passwords, stored at `/home/labex/project/500-worst-passwords.txt`.
3. Viewed the first 10 entries of the list:
   ```bash
   head -n 10 500-worst-passwords.txt
   ```

## What I found
- Every incorrect attempt returned the same generic message: `Invalid Username or Password!`. The page doesn't say whether the username exists or only the password is wrong.
- The wordlist contains the most common weak passwords. Dictionary attacks try these known passwords first instead of every possible combination, which greatly improves the odds of gaining access.
- My repeated manual attempts were themselves a basic, manual form of brute-force attack. Attackers automate the same process with wordlists to try thousands of credentials quickly.

## How I found it
- **Login behaviour:** submitted incorrect credentials by hand and compared the responses.

  ![Generic error message returned for incorrect credentials](https://github.com/user-attachments/assets/d89c03cc-042d-4fb6-a994-9e5178f7ae51)

- **Wordlist contents:** read the first lines of the file with `head`.

  ![First 10 lines of 500-worst-passwords.txt](https://github.com/user-attachments/assets/3e87cb6b-34bf-4723-827e-c2bd7230340a)

## Fix/remediation
Controls identified in the lab that defend against this kind of attack:
- Generic login error messages that don't reveal which field was wrong.
- CAPTCHAs and account lockouts to stop automated attempts.
- Password requirements that prevent the weak, common passwords found in wordlists like this one.

## Tools used
- LabEx guided lab environment
- `head` (Linux)

> **Status:** This writeup covers the preparation stage only. The automated attack with Hydra hasn't been run yet; this writeup will be extended once it has.
