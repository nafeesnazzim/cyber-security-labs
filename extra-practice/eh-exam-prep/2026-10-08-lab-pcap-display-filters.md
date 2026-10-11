---
title: "Wireshark Display Filters That Matter: Hosts, HTTP, DNS, TCP Flags and Frame Ranges"
attack: [T1105, T1021.002, T1071.001]
tools: [wireshark]
---

# Wireshark Display Filters That Matter: Hosts, HTTP, DNS, TCP Flags and Frame Ranges

## Objective

Build a short, reusable cheat-sheet of display filters and prove each one against a real capture: a 9,936-packet training pcap (Unit 42 Wireshark quiz, dated 2023-03-07) from an Active Directory lab network. Extra-practice track for my Ethical Hacking module's practical exam, so the goal is speed: type the filter, read the answer.

## What I did

I grouped the filters by what they answer, wrote them in my notebook, then ran every one against the capture and screenshotted the result.

| Group | Filter |
|---|---|
| Host | `ip.addr == 172.16.1.137`, `ip.addr == 172.16.1.16`, `ip.addr == 62.173.149.243`, `ip.addr == 62.173.140.103 \|\| ip.addr == 62.173.138.138`, `ip.addr == 46.8.19.32 && tcp.port == 445`, `ip.addr == 193.233.175.18` |
| HTTP | `http.request`, `http.request.method == "POST"`, `http.request.uri contains "/drew/"`, `http.request.uri contains ".rar"`, `http.host contains "unapromo"`, `http.response.code == 200` |
| DNS | `dns.qry.name contains "pcapworkshop"`, `... contains "wpad"`, `... contains "microsoft"` |
| TCP flags | `tcp.flags.syn == 1 && tcp.flags.ack == 0`, `tcp.flags.syn == 1 && tcp.flags.ack == 1`, `tcp.flags.reset == 1`, `tcp.analysis.retransmission` |
| Other | `arp`, `arp.opcode == 1`, `icmp`, `frame.len > 1000`, `tcp.port == 88 \|\| tcp.port == 389` |
| Frame ranges | `frame.number >= 2341 && frame.number <= 2475`, `frame.number >= 2492 && frame.number <= 6817`, `frame.number >= 3594 && frame.number <= 6844` |

The hostnames and addresses in the host group came from reading the capture first; the frame ranges bracket the interesting bursts I found with the other filters.

## What I found

All times are 2023-03-07, capture clock.

- **The victim workstation is 172.16.1.137** (`DESKTOP-3GJL3PV`). It is in 9,829 of the 9,936 packets (98.9 %). The domain controller is 172.16.1.16 (`PCAPWORKSHOP-DC`, domain `pcapworkshop.net`), 1,651 packets.
- **Direct download of archives over plain HTTP:** from 62.173.149.243 (`free.ds`) the workstation fetched `/stilak32.rar`, `/stilak64.rar` at 07:37:19 and `/cook32.rar`, `/cook64.rar` at 07:38:18, each answered `200 OK (application/x-rar-compressed)`.
- **Earlier download:** `GET /mise/Cliente.zip` from `unapromo.com` at 07:31:56, answered `200 OK (application/zip)` in the next frame.
- **SMB to a public address, 29 seconds later:** at 07:32:25 the workstation opened TCP 445 to **46.8.19.32** (a public IP, not the domain controller). The session did an NTLMSSP exchange, then tree-connected `\\46.8.19.32\IPC$` and `\\46.8.19.32\mise`. Authentication used `PCAPWORKSHOP\DESKTOP-3GJL3PV$` first, then the domain user `PCAPWORKSHOP\sherita.kolb`. Later in the same conversation there are repeated Create/Close requests for `server.exe`, and a Create Request for `server.dbg`.
- **`/drew/` beaconing pattern:** 60 packets match `http.request.uri contains "/drew/"`. Each request is a GET (or POST) to a long random-looking path under `/drew/`, sent to a different hostname or address each time. From about 07:40 to 08:02 the requests arrive roughly once a minute, each answered `200 OK`.
- **Three POSTs** (07:37:31, 07:37:38, 07:38:31) went to the same host (`avigroup2.unassigned.planethost...`); the first POST was retransmitted three times and drew duplicate ACKs.
- **DNS:** 52 packets involve `pcapworkshop`, 20 are `wpad` lookups that all came back "No such name" (SOA from the DC), and 46 involve `microsoft` (Windows telemetry and update names). The `wpad` failures are normal Windows proxy auto-discovery noise, so they are baseline rather than malicious.
- **TCP flags:** 173 SYN+ACK packets; 108 reset packets (a burst against Google, Akamai and Microsoft hosts at 07:32:05, shortly after the 07:31:56 download, then resets to and from the DC on ports 88, 135, 389 and 445); 34 retransmissions. Connections to **193.233.175.18** never completed: three separate attempts (07:50:27, 07:51:32, 08:03:56), each a SYN, two retransmitted SYNs, then a RST/ACK from the target. That is 12 packets in total.
- **Large frames:** 3,531 packets (35.5 %) are longer than 1,000 bytes; the first rows are TLS Application Data from `www.google.com`, so size alone is not suspicious here.
- **Domain traffic:** 614 packets on ports 88 or 389 are normal Kerberos and LDAP between the workstation and the DC (LDAP bind and search for the machine's own computer object).
- **ARP:** 105 ARP packets, 54 of them requests; ordinary "who has 172.16.1.1 / .16 / .137" traffic between the workstation, DC and gateway.

My notes list the filters but do not record a verdict on what the traffic is. The sequence above (archive and zip downloads over HTTP, SMB to an external IP, periodic GETs to many different hosts) is what a defender would call suspicious; I have not identified the malware family and do not claim to.

## How I found it

### Host filters

![ip.addr == 172.16.1.137, 9,829 of 9,936 packets displayed](images/pcap-filters/hosts/1.png)

![ip.addr == 172.16.1.16, 1,651 packets: DNS to the domain controller](images/pcap-filters/hosts/2.png)

![ip.addr == 62.173.149.243: TCP handshake then GET /stilak32.rar](images/pcap-filters/hosts/3.png)

![Two other public addresses: GETs under /drew/ with a retransmitted POST and duplicate ACKs](images/pcap-filters/hosts/4.png)

![ip.addr == 46.8.19.32 && tcp.port == 445: SMB2 Create and Close requests for server.exe](images/pcap-filters/hosts/5.png)

![ip.addr == 193.233.175.18: three SYN attempts with retransmissions and RST/ACK](images/pcap-filters/hosts/6.png)

### HTTP filters

![http.request: 38 requests](images/pcap-filters/http/1.png)

![http.request.method == POST: three POSTs to the same host](images/pcap-filters/http/2.png)

![http.request.uri contains /drew/: 60 packets](images/pcap-filters/http/3.png)

![http.request.uri contains .rar: four archive downloads, each 200 OK](images/pcap-filters/http/4.png)

![http.host contains unapromo: GET /mise/Cliente.zip](images/pcap-filters/http/5.png)

![http.response.code == 200: the first response is application/zip from unapromo.com](images/pcap-filters/http/6.png)

### DNS filters

![dns.qry.name contains pcapworkshop, including SRV lookups for _ldap._tcp and _kerberos._tcp](images/pcap-filters/dns/1.png)

![dns.qry.name contains wpad: every lookup answered No such name](images/pcap-filters/dns/2.png)

![dns.qry.name contains microsoft: 46 packets of Windows telemetry and update lookups](images/pcap-filters/dns/3.png)

### TCP flag filters

![SYN without ACK: connection attempts from the workstation](images/pcap-filters/tcp/1.png)

![SYN with ACK: 173 accepted connections](images/pcap-filters/tcp/2.png)

![tcp.flags.reset == 1: 108 resets](images/pcap-filters/tcp/3.png)

![tcp.analysis.retransmission: 34 retransmissions](images/pcap-filters/tcp/4.png)

### Other filters

![arp: address resolution between the workstation, DC and gateway](images/pcap-filters/other/1.png)

![arp.opcode == 1: requests only](images/pcap-filters/other/2.png)

![frame.len > 1000: 3,531 packets, mostly TLS from Google](images/pcap-filters/other/3.png)

![tcp.port == 88 or 389: Kerberos and LDAP with the domain controller](images/pcap-filters/other/4.png)

### Frame-range filters

![Frames 2341 to 2475: the reset burst at 07:32:05](images/pcap-filters/frame-len/1.png)

![Frames 2492 to 6817: SMB session to 46.8.19.32 (NTLMSSP, IPC$ and mise tree connects)](images/pcap-filters/frame-len/2.png)

![Frames 3594 to 6844: the HTTP download and /drew/ burst](images/pcap-filters/frame-len/3.png)

## Detection

What a hunter would take from this capture:

- **Outbound SMB (445) to a public address** is almost never legitimate from a workstation. Log sources: firewall egress logs, Zeek `conn.log`, or Sysmon event 3 (network connection) on the source host. In this capture it follows a file download by under 30 seconds.
- **Archives and executables fetched over plain HTTP** (`.rar`, `.zip`, `.exe`) from an IP-addressed or low-reputation host. Proxy or Zeek `http.log`: `uri` ending in `.rar` or `.zip` with a `resp_mime_types` of an archive type, and a host that is a bare domain with no prior history.
- **Periodic requests to many different hosts under one URI prefix** (`/drew/` here) with a roughly constant interval. Hunt for this by grouping proxy logs on the first path segment and counting distinct destinations per source.
- **Unanswered SYNs** to a single external IP, repeated over time (193.233.175.18). Baseline noise, but worth listing as dead infrastructure the host keeps trying.

Syntax-checked only, not run against real logs:

```yaml
title: Outbound SMB Connection From Internal Host to Public IP Address
id: 8e2a4c10-7d35-4b6f-a1c9-03f5d6b82e47
status: experimental
description: A host opens TCP 445 to an address outside RFC 1918 space, which is rare for legitimate workstation traffic.
logsource:
    product: zeek
    service: conn
detection:
    selection:
        proto: tcp
        id.resp_p: 445
    filter_internal:
        id.resp_h|cidr:
            - 10.0.0.0/8
            - 172.16.0.0/12
            - 192.168.0.0/16
    condition: selection and not filter_internal
falsepositives:
    - Cloud file shares reached over SMB-over-internet (rare, normally blocked)
level: high
tags:
    - attack.lateral_movement
    - attack.t1021.002
```

ATT&CK, mapped from the traffic visible in the screenshots (not stated in my notes): [T1105 Ingress Tool Transfer](https://attack.mitre.org/techniques/T1105/) for the HTTP archive downloads, [T1021.002 SMB/Windows Admin Shares](https://attack.mitre.org/techniques/T1021/002/) for the `IPC$` and `mise` tree connects, and [T1071.001 Web Protocols](https://attack.mitre.org/techniques/T1071/001/) for the periodic `/drew/` requests.

## Tools used

Wireshark display filters, Statistics and the packet list and detail panes.

