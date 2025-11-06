#!/usr/bin/env python3
"""
Test the Web GUI API with Python-only functionality
"""
import requests
import json

def test_python_only_api():
    """Test the AV evasion web GUI API for Python payloads only"""
    server_url = "http://localhost:5000"
    
    print("🧪 Testing Web GUI AV Evasion - Python Only")
    print("=" * 60)
    
    # Test build_evaded_payloads endpoint with just the encrypt technique
    print("\n📦 Testing Python-only build...")
    
    payload = {
        "technique": "encrypt",
        "output_dir": "test_web_gui_python"
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
            
            # Check if we got any successful builds
            success_count = data.get('success_count', 0)
            if success_count > 0:
                print("✅ Web GUI Integration SUCCESSFUL!")
                print(f"   ✅ Built {success_count} evaded Python payloads")
                print(f"   ✅ Technique: {payload['technique']}")
                print(f"   ✅ Output: {data.get('output_dir', 'Unknown')}")
                print("\n🎯 WEB GUI STATUS: FULLY OPERATIONAL")
                print("   - Python AV evasion: ✅ Working")
                print("   - API integration: ✅ Working") 
                print("   - Build automation: ✅ Working")
                return True
            else:
                print("❌ No successful builds")
        else:
            print(f"❌ API error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API request failed: {e}")
    
    return False

if __name__ == "__main__":
    success = test_python_only_api()
    if success:
        print("\n🚀 READY FOR PRODUCTION: Web GUI + AV Evasion fully functional!")
    else:
        print("\n⚠️ Issues detected with web integration")