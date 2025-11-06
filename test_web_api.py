#!/usr/bin/env python3
"""
Test the Web GUI API functionality
"""
import requests
import json

def test_web_gui_api():
    """Test the AV evasion web GUI API"""
    server_url = "http://localhost:5000"
    
    print("🧪 Testing Web GUI AV Evasion API Integration")
    print("=" * 60)
    
    # Test 1: Check if server is responding
    try:
        response = requests.get(server_url, timeout=5)
        if response.status_code == 200:
            print("✅ Server is responding")
        else:
            print(f"❌ Server error: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Test 2: Test build_evaded_payloads endpoint
    print("\n📦 Testing build_evaded_payloads endpoint...")
    
    payload = {
        "technique": "encrypt",
        "output_dir": "test_web_gui_output"
    }
    
    try:
        response = requests.post(
            f"{server_url}/build_evaded_payloads",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API call successful!")
            print(f"   Success: {data.get('success', 'Unknown')}")
            print(f"   Success Count: {data.get('success_count', 0)}")
            print(f"   Failed Count: {data.get('fail_count', 0)}")
            print(f"   Output Dir: {data.get('output_dir', 'Unknown')}")
            
            # Show first few lines of output
            output = data.get('output', '')
            if output:
                lines = output.split('\n')[:5]
                print("   Build Output (first 5 lines):")
                for line in lines:
                    if line.strip():
                        print(f"     {line}")
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ API request failed: {e}")

if __name__ == "__main__":
    test_web_gui_api()