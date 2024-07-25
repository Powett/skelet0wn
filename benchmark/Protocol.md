# Protocol
For every identified scenario, provided input and goals are detailed.
Every scenario is independent from the others, please try to start each scenario from scratch!

The goal is to time the whole execution process: read the provided input and goals, then start the timer and start coding.

Please do not stop the timer
- during network traffic
- if you need time to read manuals/find wordlists/...
This is all part of the process !

Please use the specified tools and options when relevant.

Ensure beforehand that your GOAD and VPN configuration are up and running (e.g. `nxc/cme smb 192.168.56.1/27`, should return GOT-related machines up)
## 1. Nmap - NXCEnum
Provided:
- login (username:password): `samwell.tarly:Hearstbane`
- targeted subnet: `192.168.56.1/27`

Goals:
- nmap scan ports 1-500 (default arguments for threads, scripts, etc)
- Provide list of IPs having port 445 open
- Enumerate SMB shares exposed on those IP, using provided user & password
- Enumerate SMB users on the subnet, using anonymous user & password
## 2. Kerberoast
Provided:
- Domain Controller IP: `192.168.56.11`
- login `north.sevenkingdoms.local\samwell.tarly:Hearstbane`
- custom wordlist: `./needed_files/2_kerberoast_wordlist.txt`

Goals:
- Perform a Kerberoast attack using specified wordlist, domain and login, retrieve password(s).

## 3. ASREProast
Provided:
- Domain Controller IP: `192.168.56.11`
- login `north.sevenkingdoms.local\samwell.tarly:Hearstbane`

Goals:
- Perform an ASREPRoast attack using rockyou.txt wordlist (find it on your machine/download it, but remember it is part of the process!), domain and login, retrieve password(s).

## 4. Kerbrute
Provided:
- Domain Controller IP: `192.168.56.11`
- domain: `north.sevenkingdoms.local`
- custom userlist: `./needed_files/4_kerbrute_userlist.txt`

Goals:
- Enumerate valid users (without password spraying) on DC, using provided custom userlist.

## Results
Please compile your results in the following table:

| Scenario   | Your time |
| ---------- | --------- |
| NXCEnum    |           |
| Kerberoast |           |
| ASREPRoast |           |
| Kerbrute   |           |

