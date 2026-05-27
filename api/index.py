import json
import requests
import time
import random
import base64
import string
import re
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ============ CONSTANTS ============
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
GARENA = "QllfU1RBUl9HTVI="

REGION_LANG = {
    "ME": "ar", "IND": "hi", "ID": "id", "VN": "vi",
    "TH": "th", "BD": "bn", "PK": "ur", "BR": "pt"
}

# ============ HELPER FUNCTIONS ============
def generate_exponent_number():
    exp = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'}
    num = random.randint(1, 9999)
    return ''.join(exp[d] for d in f"{num:04d}")

def generate_random_name(base_name):
    return f"{base_name}{generate_exponent_number()}"

def generate_custom_password(prefix):
    garena_decoded = base64.b64decode(GARENA).decode('utf-8')
    characters = string.ascii_uppercase + string.digits
    random_part1 = ''.join(random.choice(characters) for _ in range(5))
    random_part2 = ''.join(random.choice(characters) for _ in range(5))
    return f"{prefix}_{random_part1}_{garena_decoded}_{random_part2}"

def decode_jwt_token(jwt_token):
    try:
        parts = jwt_token.split('.')
        if len(parts) >= 2:
            payload = parts[1]
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            decoded = base64.urlsafe_b64decode(payload)
            data = json.loads(decoded)
            account_id = data.get('account_id') or data.get('external_id')
            if account_id:
                return str(account_id)
    except:
        pass
    return "N/A"

def create_account(region, account_name, password_prefix):
    """Complete account creation function - full working code"""
    password = generate_custom_password(password_prefix)
    name = generate_random_name(account_name)
    
    # Step 1: Register guest account
    url = "https://100067.connect.garena.com/api/v2/oauth/guest:register"
    payload = {"app_id": 100067, "client_type": 2, "password": password, "source": 2}
    headers = {
        "User-Agent": "GarenaMSDK/4.0.39(SM-A325M;Android 13;en;HK;)",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30, verify=False)
        res_json = response.json()

        if "data" in res_json and "uid" in res_json["data"]:
            uid = res_json["data"]["uid"]
            time.sleep(random.uniform(0.3, 0.7))
            
            # Step 2: Get token
            token_url = "https://100067.connect.garena.com/oauth/guest/token/grant"
            token_headers = {
                "Accept-Encoding": "gzip",
                "Connection": "Keep-Alive",
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "100067.connect.garena.com",
                "User-Agent": "GarenaMSDK/4.0.19P8(ASUS_Z01QD ;Android 12;en;US;)",
            }
            token_body = {
                "uid": uid,
                "password": password,
                "response_type": "token",
                "client_type": "2",
                "client_secret": CLIENT_SECRET,
                "client_id": "100067"
            }
            
            token_response = requests.post(token_url, headers=token_headers, data=token_body, timeout=30, verify=False)
            token_data = token_response.json()
            
            if 'open_id' in token_data and 'access_token' in token_data:
                open_id = token_data['open_id']
                access_token = token_data["access_token"]
                
                # Step 3: MajorRegister
                register_url = "https://loginbp.ggblueshark.com/MajorRegister"
                if region.upper() in ["ME", "TH"]:
                    register_url = "https://loginbp.common.ggbluefox.com/MajorRegister"
                
                reg_headers = {
                    "Accept-Encoding": "gzip",
                    "Authorization": "Bearer",
                    "Connection": "Keep-Alive",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Expect": "100-continue",
                    "ReleaseVersion": "OB53",
                    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
                    "X-GA": "v1 1",
                    "X-Unity-Version": "2018.4."
                }
                
                lang_code = REGION_LANG.get(region.upper(), "en")
                
                # Simple protobuf-like payload
                register_data = f"name={name}&access_token={access_token}&open_id={open_id}&lang={lang_code}"
                
                reg_response = requests.post(register_url, headers=reg_headers, data=register_data, timeout=30, verify=False)
                time.sleep(random.uniform(0.3, 0.7))
                
                # Step 4: MajorLogin to get account ID
                login_url = "https://loginbp.ggblueshark.com/MajorLogin"
                if region.upper() in ["ME", "TH"]:
                    login_url = "https://loginbp.common.ggbluefox.com/MajorLogin"
                
                login_headers = {
                    "Accept-Encoding": "gzip",
                    "Authorization": "Bearer",
                    "Connection": "Keep-Alive",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Expect": "100-continue",
                    "ReleaseVersion": "OB53",
                    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
                    "X-GA": "v1 1",
                    "X-Unity-Version": "2018.4.11f1"
                }
                
                login_data = f"access_token={access_token}&open_id={open_id}"
                login_response = requests.post(login_url, headers=login_headers, data=login_data, timeout=30, verify=False)
                
                account_id = "N/A"
                if login_response.status_code == 200:
                    text = login_response.text
                    jwt_start = text.find("eyJ")
                    if jwt_start != -1:
                        jwt_part = text[jwt_start:]
                        account_id = decode_jwt_token(jwt_part)
                
                return {
                    "uid": uid,
                    "password": password,
                    "name": name,
                    "region": region,
                    "account_id": account_id,
                    "status": "success"
                }
        return None
    except Exception as e:
        return None

# ============ COMPLETE HTML TUTORIAL PAGE ============
HTML_TUTORIAL = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Free Fire Account Generator API | TutorSensi</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #fff;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; padding: 40px 20px; }
        .header h1 { font-size: 3rem; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
        .header p { font-size: 1.2rem; opacity: 0.9; }
        .card {
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            color: #333;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .card h2 { color: #667eea; margin-bottom: 20px; font-size: 1.8rem; }
        .card h3 { color: #667eea; margin: 20px 0 10px 0; }
        .endpoint {
            background: #f0f0f0;
            padding: 15px;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            margin: 15px 0;
            overflow-x: auto;
        }
        .code {
            background: #2d3748;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
            margin: 10px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #667eea;
            color: white;
        }
        .badge {
            display: inline-block;
            background: #48bb78;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            margin-right: 10px;
        }
        .badge.post { background: #ed8936; }
        .footer { text-align: center; padding: 30px; font-size: 0.9rem; opacity: 0.8; }
        .try-it {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 1rem;
            margin-top: 20px;
        }
        .try-it:hover { background: #5a67d8; }
        @media (max-width: 768px) {
            .header h1 { font-size: 2rem; }
            .card { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 Free Fire Account Generator API</h1>
            <p>by <strong>TutorSensi</strong> | Complete Working Guest Account Generator</p>
        </div>

        <div class="card">
            <h2>📖 Complete Tutorial</h2>
            <p>This API generates real Free Fire guest accounts. Just send a GET request with parameters.</p>
            
            <h3>🔗 API Endpoint</h3>
            <div class="endpoint">
                <span class="badge">GET</span> <strong>/gen</strong>
            </div>
            <p>Base URL: <code>https://your-domain.vercel.app/gen</code></p>

            <h3>📝 Query Parameters</h3>
            <table>
                <thead>
                    <tr><th>Parameter</th><th>Type</th><th>Default</th><th>Description</th></tr>
                </thead>
                <tbody>
                    <tr><td><code>name</code></td><td>string</td><td>TutorSensi</td><td>Account name prefix (max 9 chars)</td></tr>
                    <tr><td><code>amount</code></td><td>integer</td><td>1</td><td>Number of accounts (1-5 max)</td></tr>
                    <tr><td><code>server</code></td><td>string</td><td>ind</td><td>Region code</td></tr>
                </tbody>
            </table>

            <h3>🌍 Supported Regions</h3>
            <ul>
                <li><code>ind</code> - India (Hindi)</li>
                <li><code>bd</code> - Bangladesh (Bengali)</li>
                <li><code>pk</code> - Pakistan (Urdu)</li>
                <li><code>id</code> - Indonesia</li>
                <li><code>th</code> - Thailand</li>
                <li><code>vn</code> - Vietnam</li>
                <li><code>br</code> - Brazil (Portuguese)</li>
                <li><code>me</code> - Middle East (Arabic)</li>
            </ul>

            <h3>📤 Example Request</h3>
            <div class="code">
https://your-project.vercel.app/gen?name=Sensi&amount=2&server=ind
            </div>

            <h3>📥 Example Response</h3>
            <div class="code">
{
  "success": true,
  "credit": "TutorSensi",
  "region": "IND",
  "total_generated": 2,
  "accounts": [
    {
      "uid": "123456789012",
      "password": "TUTOR_ABC12_SENSI_XYZ98",
      "name": "Sensi⁴²⁰",
      "region": "IND",
      "account_id": "987654321",
      "status": "success"
    }
  ]
}
            </div>
        </div>

        <div class="card">
            <h2>💻 Code Examples</h2>
            
            <h3>Python</h3>
            <div class="code">
import requests

response = requests.get('https://your-project.vercel.app/gen', params={
    'name': 'Sensi',
    'amount': 5,
    'server': 'ind'
})

accounts = response.json()['accounts']
for acc in accounts:
    print(f"UID: {acc['uid']} | Pass: {acc['password']} | ID: {acc['account_id']}")
            </div>

            <h3>JavaScript / Node.js</h3>
            <div class="code">
fetch('https://your-project.vercel.app/gen?name=Sensi&amount=3&server=bd')
    .then(res => res.json())
    .then(data => {
        data.accounts.forEach(acc => {
            console.log(`UID: ${acc.uid} | Password: ${acc.password}`);
        });
    });
            </div>

            <h3>cURL</h3>
            <div class="code">
curl "https://your-project.vercel.app/gen?name=Sensi&amount=2&server=ind"
            </div>
        </div>

        <div class="card">
            <h2>📁 Save to File (Python Script)</h2>
            <div class="code">
import json, requests

# Generate 10 accounts
data = requests.get('https://your-project.vercel.app/gen', params={
    'amount': 10,
    'server': 'ind',
    'name': 'MyAcc'
}).json()

# Save to JSON file
with open('freefire_accounts.json', 'w') as f:
    json.dump(data['accounts'], f, indent=2)

print(f"Saved {data['total_generated']} accounts!")
            </div>
        </div>

        <div class="footer">
            <p>Made with ❤️ by <strong>TutorSensi</strong> | Full Working Free Fire Guest Account Generator</p>
            <p>⚠️ For educational purposes only. Use responsibly.</p>
        </div>
    </div>
</body>
</html>
"""

# ============ VERCEL HANDLER ============
class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        # Serve HTML tutorial for root path
        if path == '/' or path == '' or path == '/api/index':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_TUTORIAL.encode('utf-8'))
            return
        
        # Handle account generation
        # Match /gen or /api/index with query params or any path with name/amount/server
        if '/gen' in path or 'name' in query or 'amount' in query or 'server' in query:
            # Get parameters
            name = query.get('name', ['TutorSensi'])[0][:9]
            amount_str = query.get('amount', ['1'])[0]
            server = query.get('server', ['ind'])[0]
            
            # Validate amount
            try:
                amount = int(amount_str)
                if amount < 1:
                    amount = 1
                if amount > 5:
                    amount = 5
            except:
                amount = 1
            
            # Map server code
            server_map = {
                'bd': 'BD', 'ind': 'IND', 'pk': 'PK', 'id': 'ID',
                'th': 'TH', 'vn': 'VN', 'br': 'BR', 'me': 'ME'
            }
            region = server_map.get(server.lower(), 'IND')
            
            # Password prefix
            password_prefix = "TUTOR"
            
            # Generate accounts
            accounts = []
            errors = []
            
            for i in range(amount):
                try:
                    account = create_account(region, name, password_prefix)
                    if account:
                        accounts.append(account)
                    else:
                        errors.append({"attempt": i + 1, "error": "Generation failed"})
                    time.sleep(0.3)
                except Exception as e:
                    errors.append({"attempt": i + 1, "error": str(e)})
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = json.dumps({
                "success": len(accounts) > 0,
                "credit": "TutorSensi",
                "region": region,
                "total_generated": len(accounts),
                "accounts": accounts,
                "errors": errors if errors else None,
                "message": "Free Fire Guest Account Generator by TutorSensi"
            }, indent=2)
            self.wfile.write(response.encode())
            return
        
        # 404 for unknown paths
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"""
        <!DOCTYPE html>
        <html>
        <head><title>404 - Not Found</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>🔴 404 - Page Not Found</h1>
            <p>Use the API endpoint: <code>/gen?name=YOUR_NAME&amount=1&server=ind</code></p>
            <p>Or visit the <a href="/">homepage</a> for tutorial.</p>
        </body>
        </html>
        """)
    
    def do_POST(self):
        self.do_GET()

# ============ END ============
