import json
import requests
import time
import random
import base64
import string
from urllib.parse import parse_qs

# ============ CONSTANTS ============
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
GARENA = "QllfU1RBUl9HTVI="

REGION_CONFIG = {
    'IND': {'major_login_url': 'https://loginbp.common.ggbluefox.com/MajorLogin'},
    'BD': {'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin'},
    'PK': {'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin'},
    'ID': {'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin'},
    'TH': {'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin'},
    'VN': {'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin'},
    'BR': {'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin'},
    'ME': {'major_login_url': 'https://loginbp.common.ggbluefox.com/MajorLogin'}
}

# ============ HELPER FUNCTIONS ============
def generate_exponent_number():
    exp = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'}
    num = random.randint(1, 9999)
    return ''.join(exp[d] for d in f"{num:04d}")

def generate_random_name(base):
    return f"{base}{generate_exponent_number()}"

def generate_password():
    garena_decoded = base64.b64decode(GARENA).decode('utf-8')
    chars = string.ascii_uppercase + string.digits
    r1 = ''.join(random.choice(chars) for _ in range(5))
    r2 = ''.join(random.choice(chars) for _ in range(5))
    return f"TUTOR_{r1}_{garena_decoded}_{r2}"

def decode_jwt_token(jwt_token):
    try:
        parts = jwt_token.split('.')
        if len(parts) >= 2:
            payload = parts[1]
            payload += '=' * ((4 - len(payload) % 4) % 4)
            decoded = base64.urlsafe_b64decode(payload).decode('utf-8')
            data = json.loads(decoded)
            return str(data.get('account_id') or data.get('external_id', 'N/A'))
    except:
        pass
    return "N/A"

def create_account(region, name_prefix):
    """Main account creation function"""
    password = generate_password()
    account_name = generate_random_name(name_prefix)
    
    # Step 1: Register guest account
    url = "https://100067.connect.garena.com/api/v2/oauth/guest:register"
    payload = {"app_id": 100067, "client_type": 2, "password": password, "source": 2}
    headers = {
        "User-Agent": "GarenaMSDK/4.0.39(SM-A325M;Android 13;en;HK;)",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json"
    }
    
    resp = requests.post(url, headers=headers, json=payload, timeout=30, verify=False)
    resp_json = resp.json()
    
    if "data" not in resp_json or "uid" not in resp_json["data"]:
        raise Exception("Registration failed")
    
    uid = resp_json["data"]["uid"]
    time.sleep(random.uniform(0.3, 0.7))
    
    # Step 2: Get access token
    token_url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    token_body = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": CLIENT_SECRET,
        "client_id": "100067"
    }
    token_headers = {
        "User-Agent": "GarenaMSDK/4.0.19P8(ASUS_Z01QD;Android 12;en;US;)",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    token_resp = requests.post(token_url, headers=token_headers, data=token_body, timeout=30, verify=False)
    token_data = token_resp.json()
    
    if 'open_id' not in token_data:
        raise Exception("Token generation failed")
    
    open_id = token_data['open_id']
    access_token = token_data["access_token"]
    
    # Step 3: Get account ID via MajorLogin (simplified)
    region_config = REGION_CONFIG.get(region, REGION_CONFIG['IND'])
    major_url = region_config['major_login_url']
    
    payload_data = f"access_token={access_token}&open_id={open_id}"
    
    major_headers = {
        'X-Unity-Version': '2018.4.11f1',
        'ReleaseVersion': 'OB53',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD)',
    }
    
    major_resp = requests.post(major_url, headers=major_headers, data=payload_data, timeout=30, verify=False)
    
    account_id = "N/A"
    if major_resp.status_code == 200:
        text = major_resp.text
        jwt_start = text.find("eyJ")
        if jwt_start != -1:
            jwt_token = text[jwt_start:]
            account_id = decode_jwt_token(jwt_token)
    
    return {
        "uid": uid,
        "password": password,
        "name": account_name,
        "region": region,
        "account_id": account_id
    }

# ============ HTML TUTORIAL PAGE ============
HTML_TUTORIAL = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Free Fire Account Generator API | TutorSensi</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #fff;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            padding: 40px 20px;
        }
        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        .card {
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            color: #333;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .card h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8rem;
        }
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
            padding: 4px 8px;
            border-radius: 5px;
            font-size: 0.8rem;
            margin-right: 10px;
        }
        .footer {
            text-align: center;
            padding: 30px;
            font-size: 0.9rem;
            opacity: 0.8;
        }
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
            <p>by <strong>TutorSensi</strong> | Free & Unlimited Guest Account Generation</p>
        </div>

        <div class="card">
            <h2>📖 Tutorial</h2>
            <p>This API allows you to generate Free Fire guest accounts programmatically. Just send a GET request with your parameters.</p>
            
            <h3>🔗 Endpoint</h3>
            <div class="endpoint">
                <span class="badge">GET</span> <strong>/gen</strong>
            </div>
            <p>Full URL: <code>https://your-domain.vercel.app/gen</code></p>

            <h3>📝 Parameters</h3>
            <table>
                <thead>
                    <tr><th>Parameter</th><th>Type</th><th>Default</th><th>Description</th></tr>
                </thead>
                <tbody>
                    <tr><td><code>name</code></td><td>string</td><td>TutorSensi</td><td>Account name prefix (max 9 chars)</td></tr>
                    <tr><td><code>amount</code></td><td>integer</td><td>1</td><td>Number of accounts to generate (1-5)</td></tr>
                    <tr><td><code>server</code></td><td>string</td><td>ind</td><td>Region: <code>ind, bd, pk, id, th, vn, br, me</code></td></tr>
                </tbody>
            </table>

            <h3>🌍 Server Codes</h3>
            <ul>
                <li><code>ind</code> - India</li>
                <li><code>bd</code> - Bangladesh</li>
                <li><code>pk</code> - Pakistan</li>
                <li><code>id</code> - Indonesia</li>
                <li><code>th</code> - Thailand</li>
                <li><code>vn</code> - Vietnam</li>
                <li><code>br</code> - Brazil</li>
                <li><code>me</code> - Middle East</li>
            </ul>

            <h3>📤 Example Request</h3>
            <div class="code">
                https://ff-api-tutorsensi.vercel.app/gen?name=Sensi&amount=2&server=ind
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
      "uid": "123456789",
      "password": "TUTOR_ABC12_SENSI_XYZ98",
      "name": "Sensi⁴²⁰",
      "region": "IND",
      "account_id": "987654321"
    }
  ],
  "errors": null
}
            </div>

            <h3>⚠️ Error Handling</h3>
            <p>If generation fails for some accounts, they will appear in the <code>errors</code> array. The API never refuses requests — if it crashes, Vercel will return a 500 error.</p>
        </div>

        <div class="card">
            <h2>💻 Code Examples</h2>
            
            <h3>Python</h3>
            <div class="code">
import requests<br><br>
response = requests.get('https://your-domain.vercel.app/gen', params={<br>
&nbsp;&nbsp;&nbsp;&nbsp;'name': 'Sensi',<br>
&nbsp;&nbsp;&nbsp;&nbsp;'amount': 3,<br>
&nbsp;&nbsp;&nbsp;&nbsp;'server': 'ind'<br>
})<br>
print(response.json())
            </div>

            <h3>JavaScript (Node.js)</h3>
            <div class="code">
fetch('https://your-domain.vercel.app/gen?name=Sensi&amount=2&server=ind')<br>
&nbsp;&nbsp;.then(res => res.json())<br>
&nbsp;&nbsp;.then(data => console.log(data));
            </div>

            <h3>cURL</h3>
            <div class="code">
curl "https://your-domain.vercel.app/gen?name=Sensi&amount=1&server=ind"
            </div>
        </div>

        <div class="card">
            <h2>📁 Save Generated Accounts</h2>
            <p>Use the API in your own script to save accounts to a file:</p>
            <div class="code">
import json, requests<br>
data = requests.get('https://your-domain.vercel.app/gen?amount=10').json()<br>
with open('accounts.json', 'w') as f:<br>
&nbsp;&nbsp;&nbsp;&nbsp;json.dump(data['accounts'], f, indent=2)
            </div>
        </div>

        <div class="footer">
            <p>Made with ❤️ by <strong>TutorSensi</strong> | Free Fire Guest Account Generator API</p>
            <p>⚠️ For educational purposes only. Use responsibly.</p>
        </div>
    </div>
</body>
</html>
"""

# ============ CORRECT VERCEL HANDLER ============
def handler(request, response=None):
    """
    Vercel Python runtime expects a function named 'handler'
    that takes a request dict and returns a response dict.
    """
    path = request.get('path', '/')
    method = request.get('method', 'GET')
    query = request.get('query', {})
    
    # Serve HTML tutorial for root path
    if method == 'GET' and (path == '/' or path == '/api/index') and not query:
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/html; charset=utf-8"},
            "body": HTML_TUTORIAL
        }
    
    # Handle /gen endpoint
    if path in ['/gen', '/api/index'] or query:
        name = query.get('name', ['TutorSensi'])[0][:9]
        amount = query.get('amount', ['1'])[0]
        server = query.get('server', ['ind'])[0]
        
        try:
            count = min(max(1, int(amount)), 5)
        except:
            count = 1
        
        server_map = {
            'bd': 'BD', 'ind': 'IND', 'pk': 'PK', 'id': 'ID',
            'th': 'TH', 'vn': 'VN', 'br': 'BR', 'me': 'ME'
        }
        region = server_map.get(server.lower(), 'IND')
        
        accounts = []
        errors = []
        
        for i in range(count):
            try:
                account = create_account(region, name)
                accounts.append(account)
                time.sleep(0.5)
            except Exception as e:
                errors.append({"attempt": i + 1, "error": str(e)})
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "success": len(accounts) > 0,
                "credit": "TutorSensi",
                "region": region,
                "total_generated": len(accounts),
                "accounts": accounts,
                "errors": errors if errors else None
            })
        }
    
    # Redirect any unknown path to root
    return {
        "statusCode": 302,
        "headers": {"Location": "/"},
        "body": ""
    }
