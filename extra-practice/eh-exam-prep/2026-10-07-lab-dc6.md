---
title: "VulnHub DC-6: WordPress Credential Stuffing to Root via nmap NSE and NOPASSWD tar"
attack: [T1595.001, T1190, T1110.002, T1078, T1059.004, T1068, T1552.001]
tools: [arp-scan, nmap, wpscan, searchsploit, ssh]
---

# VulnHub DC-6: WordPress Credential Stuffing to Root via nmap NSE and NOPASSWD tar

## Objective

Full compromise of VulnHub's "DC: 6" boot2root VM, on an isolated VirtualBox host-only network
against my own Kali attack box. One flag, root required.

## What I did

1. Host discovery and a full scan:
   ```
   arp-scan -l
   nmap -A dc-6
   ```
   Two ports: 22/tcp (OpenSSH 7.4p1) and 80/tcp (Apache 2.4.25), which redirected to a virtual
   host, `wordy`. Added `192.168.56.118 wordy` to `/etc/hosts`.

2. The site is a WordPress install ("Wordy"). Ran WPScan for plugins, themes and users:
   ```
   wpscan --url http://wordy/ --enumerate p --enumerate t --enumerate u
   ```
   Five users enumerated: `admin`, `graham`, `mark`, `sarah`, `jens`.

3. Built a small password list by filtering `rockyou.txt` for a pattern the box hints at
   (`k01`-style passwords), and ran WPScan's own password-attack mode against all five usernames:
   ```
   wpscan --url http://wordy/ -U users.txt -P passwords.txt
   ```
   One valid combination came back: `mark`, cracked from the `k01`-pattern wordlist.

4. Logged into `/wp-admin` as `mark`. The dashboard includes a **Plainview Activity Monitor**
   plugin, which exposes an admin-only "IP tools" page (Lookup/Convert) under **Activity Monitor →
   Tools**.

5. Plainview Activity Monitor 20161228 is vulnerable to authenticated OS command injection
   (CVE-2018-15877) — the `ip` field passed to the Lookup action is not sanitised:
   ```
   searchsploit -m 45274
   ```
   Built a minimal PoC HTML form locally (`shell.html`) reproducing the exploit's hidden-field
   payload, pointed at the live Wordy install and a reverse-shell one-liner in the `ip` field,
   then opened it in Firefox and clicked **Submit request**.

6. Caught a reverse shell as `www-data`, confirmed with `whoami`/`id`.

7. Enumeration as `www-data`: `/home` listed four users (`graham`, `jens`, `mark`, `sarah`). A
   `su graham` attempt using the same `k01`-pattern password style as the WordPress credential
   succeeded, after finding a plaintext hint — `graham`'s own "things to do" note under
   `/home/mark/stuff/` recorded the exact password used when his account was created.

8. SSH'd in directly as `graham` with that recovered password, then `sudo -l`:
   ```
   User graham may run the following commands on dc-6:
       (jens) NOPASSWD: /home/jens/backups.sh
   ```
   `sudo -u jens /home/jens/backups.sh` is runnable with no password. The script
   (`tar -czf backups.tar.gz /var/www/html`) itself failed on permissions, but it's a script
   **graham can edit** (world-writable), and `sudo` lets him run it as `jens` — a classic
   writable-script-run-as-another-user escalation.

9. Edited `/home/jens/backups.sh` to drop the `tar` line and instead launch `/bin/bash`, then ran
   it via `sudo -u jens`, landing a shell as `jens`. `sudo -l` as `jens`:
   ```
   User jens may run the following commands on dc-6:
       (root) NOPASSWD: /usr/bin/nmap
   ```

10. nmap's interactive/scripting mode is a well-known `sudo` escalation vector: nmap can load and
    execute an NSE (Nmap Scripting Engine) script, and a script can shell out via `os.execute()`.
    Wrote a one-line NSE script that just executes `/bin/sh`, then ran it as root:
    ```
    echo "os.execute('/bin/sh')" > /tmp/root.nse
    sudo nmap --script=/tmp/root.nse
    ```
    This dropped straight into a root shell.

11. Confirmed root: `whoami` → `root`, then `cd /root && cat theflag.txt` — the box's own
    congratulations banner, no `flag{}`-style token to capture.

## What I found

A four-stage privilege-escalation chain, each step reusing a weakness from the one before:

- WordPress credentials were reused from a predictable, pattern-based password scheme across the
  whole box — the same style of password was good for the `mark` WordPress account, `graham`'s
  Linux account, and was documented in plaintext in `graham`'s own notes.
- The Plainview Activity Monitor plugin's authenticated command injection (CVE-2018-15877) gave
  unauthenticated-equivalent RCE the moment any admin credential was recovered.
- A `sudo` rule let `graham` run a world-writable script as `jens` — editing the script is
  equivalent to running anything as `jens`.
- A `sudo` rule let `jens` run `nmap` as root with no restriction on `--script`, which is a
  textbook arbitrary-code-execution-as-root primitive (nmap's NSE scripting is Turing-complete
  Lua with shell-out capability).

## How I found it

**Recon and WordPress enumeration**

![ARP scan of the host-only network](images/dc6/01.png)
![nmap -A against dc-6 — SSH and Apache, vhost redirect to wordy](images/dc6/02.png)
![building a pattern-filtered password list from rockyou.txt](images/dc6/03.png)
![/etc/hosts entry for wordy](images/dc6/04.png)
![the Wordy WordPress homepage](images/dc6/05.png)
![wpscan enumerating plugins/themes — XML-RPC enabled](images/dc6/06.png)
![wpscan user enumeration — five accounts found](images/dc6/07.png)
![copying the enumerated usernames into users.txt](images/dc6/08.png)
![wpscan password attack against the five accounts](images/dc6/09.png)
![valid WordPress credential recovered for mark](images/dc6/10.png)

**Authenticated RCE via Plainview Activity Monitor**

![logging into wp-admin as mark](images/dc6/11.png)
![Activity Monitor's own audit log of the login attempts](images/dc6/12.png)
![searchsploit — Plainview Activity Monitor authenticated command injection](images/dc6/13.png)
![CVE-2018-15877 advisory and PoC details](images/dc6/14.png)
![the exploit-db PoC HTML form source](images/dc6/15.png)
![building a local shell.html targeting the live Wordy install](images/dc6/16.png)
![confirming shell.html was written to disk](images/dc6/17.png)
![shell.html opened in the browser, ready to submit](images/dc6/18.png)

**Lateral movement and privilege escalation**

![wp-admin Users list — five accounts and roles](images/dc6/19.png)
![Activity Monitor log showing mark's admin session activity](images/dc6/20.png)
![the IP tools page the exploit abuses](images/dc6/21.png)
![netcat shell caught as www-data, su to graham, finding his documented password](images/dc6/22.png)
![SSH as graham, locating the password hint under /home/mark/stuff/](images/dc6/23.png)
![sudo -l as graham — NOPASSWD on jens's backups.sh](images/dc6/24.png)
![export TERM fix before editing the script in nano](images/dc6/25.png)
![backups.sh contents before editing](images/dc6/26.png)
![running the edited script as jens via sudo](images/dc6/27.png)
![sudo -l as jens — NOPASSWD on /usr/bin/nmap](images/dc6/28.png)
![writing the NSE privesc one-liner and running nmap --script as root](images/dc6/29.png)
![root shell confirmed, flag read](images/dc6/30.png)
![root shell session, confirming flag contents](images/dc6/31.png)

## Detection

- **WordPress credential attack:** WPScan's distinctive user-agent string and a burst of
  `wp-login.php` `POST` requests cycling many passwords against a fixed set of usernames from one
  source IP — the Activity Monitor plugin's own log captured this clearly, including the scanner's
  user-agent, and a SIEM correlation rule on login-failure rate per source would catch it without
  needing the plugin at all.
- **Plainview Activity Monitor RCE (CVE-2018-15877):** a `POST` to
  `wp-admin/admin.php?page=plainview_activity_monitor&tab=activity_tools` with an `ip` parameter
  containing shell metacharacters or a piped command is unambiguous and specific to this CVE.
- **Reverse shell spawn:** `www-data` spawning a shell process — the same process-tree signature
  seen throughout this series.
- **Writable-script-as-another-user escalation:** a `sudo` rule permitting one low-privilege user
  to run a script as a *different* low-privilege user is itself the finding — a periodic `sudo -l`
  / sudoers audit, combined with ensuring any script named in a sudoers rule isn't writable by the
  grantee, closes this off entirely.
- **nmap NSE privilege escalation:** `sudo nmap --script=...` loading a script from a
  world-writable or user-controlled path, immediately followed by a shell spawning as root inside
  the `nmap` process tree, is a high-fidelity signal specific to this well-known sudo-rule misuse
  pattern (GTFOBins' entry for `nmap`).

A minimal Sigma rule for the nmap NSE privilege escalation:

```yaml
title: Nmap Spawning a Shell via Sudo
status: experimental
description: Detects nmap, run via sudo, spawning an interactive shell as root — consistent
    with GTFOBins-style sudo-rule abuse through the Nmap Scripting Engine.
logsource:
    category: process_creation
    product: linux
detection:
    selection:
        ParentImage|endswith: '/nmap'
        Image|endswith:
            - '/sh'
            - '/bash'
    condition: selection
falsepositives:
    - Legitimate NSE scripts that intentionally shell out (should be allow-listed by script path)
level: high
```

## Tools used

arp-scan, nmap (recon and, later, as the privesc vector itself), wpscan, searchsploit, a hand-built
HTML exploit form, netcat, ssh, nano.
