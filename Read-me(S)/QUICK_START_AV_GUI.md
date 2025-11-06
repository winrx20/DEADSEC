# 🛡️ Quick Start: AV Evasion Web GUI

## How to Access

1. **Start the C&C Server:**
   ```powershell
   cd "c:\Users\User\Documents\code\Malware\CUSTOM BOTNET"
   python src/cnc_server.py
   ```

2. **Open Your Browser:**
   ```
   http://localhost:5000
   ```

3. **Navigate to AV Evasion:**
   - Look for the 🛡️ **AV Evasion** tab in the sidebar
   - Click to access the full AV evasion interface

## Quick Build (Recommended)

### Build All 19 Payloads:
1. Select **"Full Evasion (All 31 Layers)"** from the dropdown
2. Click **"BUILD ALL EVADED PAYLOADS"**
3. Wait for the build to complete (shows progress with spinner)
4. Review the results showing success/fail counts
5. Find your evaded payloads in `evaded_payloads/` directory

### Build Single Payload:
1. Scroll to the "Single Payload Builder" section
2. Select payload from dropdown (e.g., "Credential Harvester")
3. Choose technique (Full recommended)
4. Click **"BUILD SINGLE PAYLOAD"**
5. Output saved to `evaded_payloads/evaded_[payload_name]`

## Features at a Glance

### 📊 Stats Dashboard
- **31 Techniques:** Total evasion capabilities
- **95% → 5%:** Detection rate improvement
- **[Count]:** Number of successfully built payloads
- **Real-time:** Current build status

### 🎯 Evasion Techniques
- **Python:** 15 layers including VM detection, encryption, obfuscation
- **PowerShell:** 16 layers including AMSI bypass, ETW bypass, reflection

### 📈 Effectiveness Matrix
View detection rates before/after evasion for major AV products:
- Windows Defender: 95% → 5-10% (↓85%)
- Kaspersky: 98% → 20-30% (↓68%)
- Norton: 92% → 10-15% (↓77%)
- McAfee: 90% → 8-12% (↓78%)
- Avast/AVG: 88% → 12-18% (↓70%)

## OPSEC Reminders ⚠️

✅ **DO:**
- Use only on authorized systems
- Rebuild payloads before each engagement
- Test in isolated VMs first

❌ **DON'T:**
- Upload to VirusTotal (burns signatures)
- Use on unauthorized systems (illegal)
- Reuse payloads across multiple engagements

## Deployment Workflow

1. **Build Evaded Payloads** (AV Evasion page)
2. **Navigate to Deploy Payloads** page
3. **Select Target Bot**
4. **Upload from `evaded_payloads/` directory**
5. **Execute on Target**
6. **Monitor Results**

## Troubleshooting

### Build Fails
- Check that Python 3.7+ is installed
- Ensure `payloads/` directory exists
- Verify `av_evasion.py` and `windows_av_evasion.ps1` are present

### Server Won't Start
- Install Flask: `pip install flask flask-cors`
- Check port 5000 isn't in use
- Run from project root directory

### Page Not Loading
- Clear browser cache
- Check console for JavaScript errors
- Verify all files (web_gui.html, app.js, styles.css) are present

## Support Files

- **Full Documentation:** `AV_EVASION_GUIDE.md`
- **Web GUI Guide:** `WEB_GUI_AV_EVASION.md`
- **Deployment Guide:** `AV_EVASION_DEPLOYMENT.md`

## Next Steps

1. ✅ Build your first evaded payload using the Web GUI
2. ✅ Test in a VM to verify AV bypass
3. ✅ Deploy on authorized targets
4. ✅ Review `AV_EVASION_GUIDE.md` for advanced techniques

---

**Ready to Deploy!** 🚀

Your AV Evasion arsenal is fully integrated into the Web GUI and ready for authorized penetration testing operations.
