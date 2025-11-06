# Red Team Engagement Checklist

## Pre-Engagement

### Authorization & Legal
- [ ] Written authorization obtained from client
- [ ] Scope of engagement clearly defined
- [ ] Rules of engagement documented
- [ ] Emergency contact procedures established
- [ ] Data handling procedures agreed upon
- [ ] Legal review completed (if required)

### Technical Preparation
- [ ] C&C server infrastructure set up
- [ ] Firewall rules configured
- [ ] DNS/domain configured (if using)
- [ ] SSL/TLS certificates obtained (if using HTTPS)
- [ ] Backup communication channels established

### Payload Preparation
- [ ] All dependencies installed (`pip install flask paramiko requests`)
- [ ] Framework tested with `python test_framework.py`
- [ ] Payloads configured with `build_payload.py`
- [ ] C&C server IP/domain set in all agents
- [ ] SSH credentials prepared
- [ ] Payloads renamed/obfuscated (if required)

### Operational Security
- [ ] VPN/proxy configured
- [ ] Attribution removed from payloads
- [ ] Log collection configured
- [ ] Secure data storage prepared
- [ ] Cleanup procedures documented

---

## Initial Access Phase

### C&C Server Deployment
- [ ] C&C server started: `python src/cnc_server.py`
- [ ] Server accessibility verified from external network
- [ ] Firewall rules tested
- [ ] API endpoints tested (add_bot, send_command)

### Agent Deployment
- [ ] Initial access vector identified
- [ ] Appropriate agent selected (Python/Bash/PowerShell)
- [ ] Agent deployed to target
- [ ] Agent execution confirmed
- [ ] Bot registration verified in C&C
- [ ] Persistence mechanism confirmed

### Initial Verification
- [ ] Command execution tested
- [ ] File upload tested
- [ ] File download tested
- [ ] Connection stability verified
- [ ] Beacon functionality confirmed

---

## Reconnaissance Phase

### Network Mapping
- [ ] `network_scanner.py` deployed
- [ ] Local network hosts identified
- [ ] Open ports documented
- [ ] Services identified
- [ ] Potential lateral movement targets noted

### Privilege Escalation Assessment
- [ ] `privesc_checker.py` executed
- [ ] Privilege escalation vectors identified
- [ ] Sudo/admin permissions checked
- [ ] SUID binaries enumerated (Linux)
- [ ] Unquoted service paths checked (Windows)
- [ ] Findings documented

### System Information
- [ ] OS version collected
- [ ] Installed software inventoried
- [ ] Running services documented
- [ ] User accounts enumerated
- [ ] Network configuration collected

---

## Credential Harvesting Phase

### Automated Harvesting
- [ ] `credential_harvester.py` deployed
- [ ] Browser passwords extracted
- [ ] SSH keys collected
- [ ] WiFi passwords harvested (Windows)
- [ ] Saved credentials extracted
- [ ] Results exfiltrated via C&C

### Active Monitoring
- [ ] `keylogger.py` deployed on high-value targets
- [ ] Logging duration determined
- [ ] Output file location confirmed
- [ ] Keylog data collected periodically

### Credential Testing
- [ ] Harvested credentials documented
- [ ] Credentials tested for validity
- [ ] Privileged accounts identified
- [ ] Lateral movement opportunities noted

---

## Surveillance Phase

### Screen Monitoring
- [ ] `screenshot_capture.py` deployed
- [ ] Capture interval configured
- [ ] Storage location verified
- [ ] Screenshots collected periodically
- [ ] Sensitive information identified

### Activity Monitoring
- [ ] User login times noted
- [ ] Application usage monitored
- [ ] Network activity observed
- [ ] Sensitive operations documented

---

## Data Exfiltration Phase

### File Collection
- [ ] `file_exfiltrator.py` deployed
- [ ] Search patterns configured
- [ ] Sensitive file locations identified
- [ ] Files collected and archived
- [ ] Archive created successfully

### Data Transfer
- [ ] Archive(s) downloaded via C&C `download_file`
- [ ] File integrity verified
- [ ] Data stored securely
- [ ] Backup copies created
- [ ] Original files handled per rules of engagement

### Data Analysis
- [ ] Collected data inventoried
- [ ] Sensitive information identified
- [ ] Findings categorized
- [ ] Evidence documented
- [ ] Report preparation started

---

## Lateral Movement Phase (if in scope)

### Target Selection
- [ ] Additional targets identified from recon
- [ ] Access methods determined
- [ ] Credentials prepared
- [ ] Deployment method selected

### Deployment
- [ ] Agents deployed to additional systems
- [ ] New bots registered in C&C
- [ ] Persistence established
- [ ] Access verified

---

## Privilege Escalation Phase (if in scope)

### Vector Exploitation
- [ ] Privilege escalation method selected
- [ ] Exploit tested in lab (if possible)
- [ ] Exploit executed on target
- [ ] Elevated privileges confirmed
- [ ] Actions documented

### Post-Escalation
- [ ] Additional access obtained
- [ ] New credentials harvested
- [ ] Domain admin rights assessed (if applicable)
- [ ] Further objectives pursued

---

## Cleanup Phase

### Payload Removal
- [ ] All running payloads stopped
- [ ] Payload files deleted from targets
- [ ] Temporary files removed
- [ ] Hidden copies deleted

### Persistence Removal
**Linux:**
- [ ] Systemd services stopped and removed
- [ ] Cron jobs removed
- [ ] Shell RC modifications removed
- [ ] User systemd services removed

**Windows:**
- [ ] Registry Run keys removed
- [ ] Scheduled tasks deleted
- [ ] Startup folder items removed
- [ ] VBScript wrappers deleted

**macOS:**
- [ ] LaunchAgents removed
- [ ] Cron jobs removed
- [ ] Shell RC modifications removed

### Log Cleanup (if in scope)
- [ ] Command history cleared
- [ ] Application logs reviewed
- [ ] System logs addressed per agreement
- [ ] Audit logs handled per agreement

### Verification
- [ ] All persistence mechanisms removed
- [ ] No payloads remaining
- [ ] System state verified
- [ ] Client notified of cleanup completion

---

## Post-Engagement

### Data Handling
- [ ] All collected data inventoried
- [ ] Sensitive data secured
- [ ] Client data handling procedures followed
- [ ] Unnecessary data deleted per agreement
- [ ] Data retention policy followed

### Documentation
- [ ] Timeline of activities created
- [ ] All commands executed documented
- [ ] Files accessed/exfiltrated listed
- [ ] Credentials obtained documented
- [ ] Screenshots/evidence organized

### Reporting
- [ ] Executive summary prepared
- [ ] Technical findings documented
- [ ] Risk ratings assigned
- [ ] Remediation recommendations provided
- [ ] Evidence referenced
- [ ] Report reviewed for quality
- [ ] Report delivered to client

### Debrief
- [ ] Client debrief session scheduled
- [ ] Findings presented
- [ ] Questions answered
- [ ] Remediation guidance provided
- [ ] Follow-up actions agreed upon

### Infrastructure Teardown
- [ ] C&C server shut down
- [ ] Logs archived securely
- [ ] Infrastructure documented
- [ ] Billing/time tracking completed

---

## Emergency Procedures

### If Detected
- [ ] Stop all active operations
- [ ] Contact emergency contact per agreement
- [ ] Document detection circumstances
- [ ] Preserve evidence
- [ ] Follow pre-agreed incident response procedure

### If System Issues Occur
- [ ] Stop operation immediately
- [ ] Notify client per agreement
- [ ] Document issue
- [ ] Assess impact
- [ ] Follow remediation procedure

### If Legal Issues Arise
- [ ] Stop all operations
- [ ] Contact legal counsel
- [ ] Preserve all documentation
- [ ] Follow legal guidance

---

## Notes Section

### Targets
```
Target 1: [IP/Hostname]
- Status: 
- Agent: 
- Access Level: 
- Notes: 

Target 2: [IP/Hostname]
- Status: 
- Agent: 
- Access Level: 
- Notes: 
```

### Credentials Obtained
```
[System] - [Username] - [Password/Key] - [Privilege Level] - [Tested: Y/N]
```

### Findings
```
Finding 1:
- Severity: 
- Description: 
- Evidence: 

Finding 2:
- Severity: 
- Description: 
- Evidence: 
```

### Issues Encountered
```
Issue 1:
- Date/Time: 
- Description: 
- Resolution: 
```

---

**Remember:** This is a professional security engagement. Maintain documentation, stay within scope, and handle all data responsibly.
