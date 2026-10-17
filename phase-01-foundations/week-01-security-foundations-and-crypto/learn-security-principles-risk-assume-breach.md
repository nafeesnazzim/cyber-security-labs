---
title: "Security principles, risk and the assume-breach mindset"
attack: []
tools: []
---

# Security principles, risk and the assume-breach mindset

## Objective
Build the vocabulary and mental models that every later week relies on: the CIA triad, identity and access, risk maths, threat modelling with STRIDE, vulnerability scoring, defence in depth and the assume-breach view of defence. I tied each idea to a real breach and to its AWS equivalent.

## What I did
1. Studied five breaches and recorded which security property each compromised, the cause and the mitigation.
2. Worked through the CIA triad, data states, access control models, the AAA steps and the asset/threat/vulnerability/risk chain.
3. Learned the vulnerability vocabulary (CVE, CWE, CVSS, EPSS, KEV, NVD) and the control frameworks and principles behind defence in depth.
4. Completed seven short labs (A to G) and a 25-question recap.

### Breach table

| Name | Compromised | Cause | Mitigation |
|---|---|---|---|
| WannaCry | Availability | Unpatched systems, flat networks | Proper patching, network segmentation |
| Equifax | Confidentiality | Unpatched, blind monitoring | Proper patching, tool inspection |
| SolarWinds | Integrity | Update with a compromised build | Double-check patches |
| Capital One | Confidentiality | No least privilege, misconfiguration | Least privilege, alerting |
| Colonial | Availability | No MFA on remote access servers | MFA |

### Core definitions
- **Confidentiality:** only authorised people can access.
- **Integrity:** data or the system is not changed or altered.
- **Availability:** the right people reach the right data at the right speed.
- **Data states:** at rest (stored somewhere; needs encryption for the device), in transit (being transferred; encryption), in use (actively processing; access control, versioning and so on).
- **Trade-offs:** confidentiality versus availability (encryption is good, but there is a risk of loss); integrity versus availability (protects production, but altering things is time-consuming); confidentiality versus visibility (encryption stops attackers, but you cannot read the traffic either).

### Identity and AAA, with AWS equivalents

| Step | AWS equivalent |
|---|---|
| Identification | An IAM username or role name |
| Authentication | Sign-in, access keys, STS tokens |
| Authorisation | IAM policies |
| Accounting | CloudTrail |

### Access control models

| Model | Idea |
|---|---|
| DAC (discretionary) | The owner decides who gets access |
| MAC (mandatory) | A central authority sets access |
| RBAC (role based) | People get roles; access is attached to the role |
| ABAC (attribute based) | Access based on user, resource and context |

### Asset, threat, vulnerability, risk (flood analogy)

| Term | Meaning | Flood analogy | AWS example |
|---|---|---|---|
| Asset | The thing worth protecting | The house and its contents | Customer data in S3 |
| Threat | Something that could cause harm | The river rising | Attackers scanning for open buckets |
| Vulnerability | A weakness that can be exploited | No flood barrier | Bucket set to public |
| Risk | Chance the threat uses the vulnerability x damage | How likely it floods x repair bill | Likelihood of discovery x cost of the leak |

### STRIDE

| Letter | Threat | Property attacked | Example |
|---|---|---|---|
| S | Spoofing | Authentication | Using a stolen password and pretending to be someone |
| T | Tampering | Integrity | Modifying a bank-transfer amount in transit |
| R | Repudiation | Non-repudiation / accountability | "I never deleted that file", with no logs to prove otherwise |
| I | Information disclosure | Confidentiality | Public bucket |
| D | Denial of service | Availability | Flooding a login endpoint |
| E | Elevation of privilege | Authorisation | A normal user becoming admin |

### Vulnerability vocabulary

| Term | What it is | Who runs it |
|---|---|---|
| CVE | A unique ID for a specific known flaw, e.g. CVE-2017-5638 | MITRE, CVE Program |
| CWE | A category of weakness, e.g. SQL injection or missing authentication | MITRE |
| CVSS | A 0 to 10 severity score for a flaw in general | FIRST |
| EPSS | A probability (0 to 1) that the flaw will be exploited in the next 30 days | FIRST |
| KEV | A catalogue of flaws confirmed exploited in the wild | CISA (US) |
| NVD | A database that enriches CVEs with scores and details | NIST |

### Assume breach
- NIST CSF 2.0 functions: Govern, Identify, Protect, Detect, Respond, Recover.
- "Prevention fails; so detect." A defender needs one catch; an attacker needs zero slips.
- The loop I drew: detect, hunt, respond, and back to detect.
- Kill chain applied to the Equifax breach: reconnaissance (found a vulnerable web app on the internet), weaponisation (used a public exploit for the Struts flaw), delivery (sent a crafted web request), exploitation (the flaw let them run commands on the server), installation (placed web shells for access), command and control (controlled the shells over the web), actions on objective (moved through the network and took data).

### Defence in depth

| Layer | What it protects | AWS example |
|---|---|---|
| People and processes | Humans | Security training, response plan |
| Perimeter and network | Traffic | Security groups, NACLs, VPC design |
| Identity | Who can act | IAM, MFA, SSO |
| Host and compute | Machines | Patching, hardened images |
| Application | Code and logic | Input validation, WAF |
| Data | The jewels | Encryption at rest, bucket policies |
| Monitoring and response | Visibility | CloudTrail, GuardDuty alerts |

Blast radius is the amount of damage a single compromise can do. "Preventive controls fail, so defensive controls matter."

### Five Ws of a good log
The six items are: when (timestamp with time zone), who (user or role), what (action), where (source IP, host, region), on what (the resource affected), and whether it worked (success or failure). Principle: baseline first, then anomalies.

### Lab D: CVE triage with real data

| Priority | CVE | Affects | CVSS | Severity | EPSS | In KEV |
|---|---|---|---|---|---|---|
| 1 | CVE-2021-44228 | Apache Log4j 2.0-beta9 through 2.15.0 | 10 | Critical | 94% | Yes |
| 2 | CVE-2017-5638 | Jakarta Multipart parser in Apache Struts 2.2.3.x before 2.3.32 and 2.5.x before 2.5.10.1 (`#cmd=string`) | 9.8 | Critical | 99.23% | Yes |
| 3 | CVE-2017-0144 | SMBv1 on Vista SP2, Server 2008 SP2 and R2 SP1, Windows 7 SP1, 8.1, Server 2012 and R2, RT 8.1, Windows 10 (Gold, 1511, 1607), Server 2016 | 8.8 | High | 99.2% | Yes |

### Lab A: homelab risk register

| ID | Asset | Threat | Likelihood | Impact | Score | P/D/C | Treatment |
|---|---|---|---|---|---|---|---|
| R-01 | Laptop | Malfunction | 7 | 8 | 56 | P | Regular maintenance |
| R-02 | Phone | Robbery | 2 | 8 | 16 | P | Be aware of surroundings |
| R-03 | LinkedIn | Hacked | 3 | 9 | 27 | P | MFA |

### Lab C: breach autopsy, Capital One
1. Property compromised: confidentiality.
2. Asset: customer information. Threat: external attacker. Vulnerabilities: misconfigured WAF and over-permissive IAM (a possible third is unconfirmed).
3. Yes, a risk: it was public facing and misconfigured, with valuable assets behind it.
4. The IAM role had more permissions than required.
5. Failed or weak controls: the WAF and IAM policies. Missing: alerting and MFA.
6. Evidence source: logs.
7. Detective control; the breach was not known to internal staff.
8. Kill chain: reconnaissance (scanning a vulnerable web app); delivery and exploitation (a crafted request exploiting the misconfigured WAF); installation (credentials, so not needed); command and control (stolen credentials being used); actions on objective (listing and copying S3 data).

### Lab B: classify the incident
1. Confidentiality: no cyber security training.
2. Integrity: no signing or verification.
3. Availability: no DDoS protection.
4. Confidentiality: no disk encryption.
5. Integrity: malicious intent.
6. Availability: backups not tested.
7. Availability and confidentiality: initial access method.
8. Vulnerability.

### Lab E: do the maths
1. SLE = £120,000 x 0.4 = £48,000; ARO = 0.5; ALE = £24,000.
2. Before: £5,000 x 6 = £30,000. After: £900 x 6 = £5,400 remaining. Reduction £24,600. Net benefit = £24,600 - £1,500 = £23,100 per year.
3. Baseline: SLE £25,000, ALE £10,000. Control A: ALE £2,500, reduction £7,500, net +£4,500 (so the control costs £3,000 a year). Control B: ALE £100,000 x 0.04 = £4,000, reduction £6,000, net -£6,000 (so the control costs £12,000 a year). Decision: buy A, because B costs more than the risk it removes.
4. ARO = 12 / 8 = 1.5; ALE = £4,000 x 1.5 = £6,000.
5. Inherent 5 x 4 = 20 (High); residual 2 x 4 = 8 (Medium).

### Lab F: STRIDE on a tiny app
I drew a data-flow diagram with a user, a server and a database bucket. Flows: log in and upload a PDF, download request, return the file. Trust boundary 1 sits between user and server; trust boundary 2 between the database bucket and the server.

| STRIDE factor | Threat | Control type | Control |
|---|---|---|---|
| Spoofing | Scanning, brute-forcing, guessing admin passwords; reusing an already infiltrated password | Preventive | Password safeguards: hashing and salting, diverse use of characters |
| Tampering | Creating, removing or updating existing user-uploaded files | Detective | Log file-alteration events if possible; create and test backups beforehand |
| Repudiation | Users denying they tampered with a file | Detective | Monitor and implement user login logs |
| Information disclosure | Without RBAC, an attacker changes the CV ID and obtains another user's CV | Preventive | Randomised, unpredictable URL formats |
| Denial of service | Attacker uploads a massive amount of files, overwhelming the DB bucket | Preventive | Ensure DDoS protections are set and working as intended |
| Elevation of privilege | Attacker crafts a malicious request that tries to reach admin accounts | Detective and preventive | Detect anomalous, possibly malicious requests; flag them; ensure RBAC and defence in depth are implemented |

### Lab G: least-privilege policy
- Allow `s3:GetObject`
- Allow `s3:PutObject`
- Allow `logs:CreateLogStream` and `logs:PutLogEvents`
- Nothing else; especially no `s3:*` and no `*` on any resources.

## What I found
- Every breach in the table maps to a property in the triad and to a missing basic control: patching, segmentation, least privilege, MFA or monitoring.
- Scoring a flaw by CVSS alone misleads. CVSS is one metric out of many; if EPSS or KEV show active exploitation, CVSS may matter less. In my triage CVE-2021-44228 ranked first (CVSS 10), and all three CVEs were in KEV.
- Risk maths gives a way to compare controls by cost against the annual loss they remove (control A was worth buying; B cost more than the risk it removed).
- Recap answers (question text not recorded):
  1. Primarily impacts the availability of a system. Double extortion is when confidentiality is impacted too: sometimes the sensitive information provided is leaked.
  2. No: the risk is low as long as no one can gain physical access to it.
  3. Threat: a factor that can cause damage or harm to a system. Vulnerability: the factor the threat exploits to get in.
  4. SLE = £80,000 x 0.5 = £40,000; ARO = 1/4 = 0.25; ALE = £10,000 per year.
  5. Preventive: MFA. Detective: log alerting. Corrective: restore from backup.
  6. Availability means only the right people have access at the right time; if everyone has access, that is a breach of confidentiality.
  7. Change the way of thinking about log inspection: think about what an attacker can possibly do with all the current logs.
  8. Reconnaissance, weaponisation, delivery.
  9. Sometimes the owner of a file can have bad intentions, or possibly do something indeliberately.
  10. Defence in depth analogy: holes or flaws in a system can persist, but with different methods of defence an attacker gets in only if all the flaws align, which is extremely rare.
  11. A product should ship with fail-safes enabled as the default, instead of leaving the user to configure everything, which is very time-consuming.
  12. CVSS is one metric out of many. If EPSS supersedes a critical amount, for example, the CVSS might not matter at all.
  13. Authorisation.
  14. CVSS: how severe in general. EPSS: how likely to be exploited in the next 30 days. KEV: confirmed exploited.
  15. There is ambiguity between who logged in and who did what; when logs are inspected, a physical person cannot be distinguished from the accounts.
  16. Repudiation.
  17. RTO: how long you can be down. RPO: how much data you can afford to lose.
  18. At rest, in transit, in use.
  19. If you are breached, customers and regulators hold you responsible, not the supplier.
  20. Wrong or unsynchronised time; logs found to have been tampered with (so use immutable logs).
  21. A baseline is what "normal operations" means; a hunter needs a sound idea of that before investigating what an anomaly could mean.
  22. Detection engineer: writes automated rules for known bad patterns. Hunter: human-led, hypothesis-driven search for what the rules could have missed.
  23-25. Dwell time: how long an attacker is inside before being found. N-day: a fix has been made; zero-day: no fix exists. Blast radius: how much damage can be done.

## How I found it
This was a study week, so the evidence is my written lab answers above, not tool output.

## Fix/remediation
Controls recorded against each breach and STRIDE threat are in the tables above: patching, segmentation, least privilege, MFA, alerting, backups, DDoS protection and logging.

## Tools used
None; paper and reasoning only.
