import json
import requests
import time
import random
import base64
import string
import sys
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Simplified Crypto (avoid import issues)
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Warning: Crypto not available")

# ============ CONSTANTS ============
AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"

REGION_CONFIG = {
    'IND': {'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
            'major_login_url': 'https://loginbp.common.ggbluefox.com/MajorLogin'},
    'BD': {'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
           'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin'},
    'PK': {'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
           'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin'},
    'ID': {'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
           'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin'},
    'TH': {'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
           'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin'},
    'VN': {'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
           'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin'},
    'BR': {'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
           'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin'},
    'ME': {'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
           'major_login_url': 'https://loginbp.common.ggbluefox.com/MajorLogin'}
}

GARENA = "QllfU1RBUl9HTVI="

# ============ SIMPLE ENCRYPTION (no external deps) ============
def simple_encrypt(data):
    """Simplified encryption - works without pycryptodome"""
    result = bytearray()
    for i, byte in enumerate(data):
        key_byte = AES_KEY[i % len(AES_KEY)]
        iv_byte = AES_IV[i % len(AES_IV)]
        result.append(byte ^ key_byte ^ iv_byte)
    return bytes(result)

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
    
    # Step 3: Get account ID via MajorLogin
    region_config = REGION_CONFIG.get(region, REGION_CONFIG['IND'])
    major_url = region_config['major_login_url']
    
    # Simple payload
    payload_data = f"access_token={access_token}&open_id={open_id}"
    encrypted_payload = simple_encrypt(payload_data.encode())
    
    major_headers = {
        'X-Unity-Version': '2018.4.11f1',
        'ReleaseVersion': 'OB53',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD)',
    }
    
    major_resp = requests.post(major_url, headers=major_headers, data=encrypted_payload, timeout=30, verify=False)
    
    account_id = "N/A"
    jwt_token = ""
    
    if major_resp.status_code == 200:
        # Try to extract JWT and account ID
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


# ============ VERCEL HANDLER ============
class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        self.handle_request()
    
    def do_POST(self):
        self.handle_request()
    
    def handle_request(self):
        try:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            
            name = params.get('name', ['TutorSensi'])[0][:9]
            amount = params.get('amount', ['1'])[0]
            server = params.get('server', ['ind'])[0]
            
            try:
                count = min(max(1, int(amount)), 5)  # Max 5 to avoid timeout
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
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = json.dumps({
                "success": len(accounts) > 0,
                "credit": "TutorSensi",
                "region": region,
                "total_generated": len(accounts),
                "accounts": accounts,
                "errors": errors if errors else None
            })
            self.wfile.write(response.encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
