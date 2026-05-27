from http.server import BaseHTTPRequestHandler
import json
import requests
import time
import random
import base64
import string
import re
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import MajorLoginRes_pb2
except ImportError:
    # Create empty placeholder if file missing
    class MajorLoginRes_pb2:
        class MajorLoginRes:
            def ParseFromString(self, data):
                pass
    MajorLoginRes_pb2.MajorLoginRes = type('MajorLoginRes', (), {'ParseFromString': lambda self, data: None})

# ============ CONSTANTS ============
AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"

REGION_LANG = {
    "ME": "ar", "IND": "hi", "ID": "id", "VN": "vi",
    "TH": "th", "BD": "bn", "PK": "ur", "BR": "pt"
}

REGION_CONFIG = {
    'IND': {'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
            'major_login_url': 'https://loginbp.common.ggbluefox.com/MajorLogin',
            'get_login_data_url': 'https://client.ind.freefiremobile.com/GetLoginData',
            'client_host': 'client.ind.freefiremobile.com'},
    'BD': {'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
           'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin',
           'get_login_data_url': 'https://clientbp.ggblueshark.com/GetLoginData',
           'client_host': 'clientbp.ggblueshark.com'},
    'PK': {'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
           'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin',
           'get_login_data_url': 'https://clientbp.ggblueshark.com/GetLoginData',
           'client_host': 'clientbp.ggblueshark.com'},
    'ID': {'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
           'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin',
           'get_login_data_url': 'https://clientbp.ggblueshark.com/GetLoginData',
           'client_host': 'clientbp.ggblueshark.com'},
    'TH': {'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
           'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin',
           'get_login_data_url': 'https://clientbp.common.ggbluefox.com/GetLoginData',
           'client_host': 'clientbp.common.ggbluefox.com'},
    'VN': {'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
           'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin',
           'get_login_data_url': 'https://clientbp.ggblueshark.com/GetLoginData',
           'client_host': 'clientbp.ggblueshark.com'},
    'BR': {'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
           'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin',
           'get_login_data_url': 'https://clientbp.ggblueshark.com/GetLoginData',
           'client_host': 'clientbp.ggblueshark.com'},
    'ME': {'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
           'major_login_url': 'https://loginbp.common.ggbluefox.com/MajorLogin',
           'get_login_data_url': 'https://clientbp.ggblueshark.com/GetLoginData',
           'client_host': 'clientbp.ggblueshark.com'}
}

GARENA = "QllfU1RBUl9HTVI="

# ============ HELPER FUNCTIONS ============
def encrypt_api(plain_text):
    try:
        plain_bytes = bytes.fromhex(plain_text)
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        from Crypto.Util.Padding import pad
        encrypted = cipher.encrypt(pad(plain_bytes, AES.block_size))
        return encrypted.hex()
    except:
        return None

def encode_string(original):
    keystream = [0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37, 0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37,
                 0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37, 0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30]
    encoded = ""
    for i in range(len(original)):
        encoded += chr(ord(original[i]) ^ keystream[i % len(keystream)])
    return encoded

def to_unicode_escaped(s):
    return ''.join(c if 32 <= ord(c) <= 126 else f'\\u{ord(c):04x}' for c in s)

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

def encode_varint(n):
    if n < 0:
        return b''
    result = []
    while True:
        byte = n & 0x7F
        n >>= 7
        if n:
            byte |= 0x80
        result.append(byte)
        if not n:
            break
    return bytes(result)

def create_proto(fields):
    packet = bytearray()
    for field_num, value in fields.items():
        if isinstance(value, int):
            field_header = (field_num << 3) | 0
            packet.extend(encode_varint(field_header))
            packet.extend(encode_varint(value))
        elif isinstance(value, str) or isinstance(value, bytes):
            field_header = (field_num << 3) | 2
            encoded_value = value.encode() if isinstance(value, str) else value
            packet.extend(encode_varint(field_header))
            packet.extend(encode_varint(len(encoded_value)))
            packet.extend(encoded_value)
        elif isinstance(value, dict):
            nested = create_proto(value)
            field_header = (field_num << 3) | 2
            packet.extend(encode_varint(field_header))
            packet.extend(encode_varint(len(nested)))
            packet.extend(nested)
    return packet

def e_aes(plain_hex):
    plain_bytes = bytes.fromhex(plain_hex)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    from Crypto.Util.Padding import pad
    return cipher.encrypt(pad(plain_bytes, AES.block_size))

def guest_token(uid, password, region='IND'):
    region_config = REGION_CONFIG.get(region, REGION_CONFIG['IND'])
    url = region_config['guest_url']
    data = {
        "uid": str(uid),
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": CLIENT_SECRET,
        "client_id": "100067",
    }
    try:
        response = requests.post(url, data=data, timeout=30, verify=False)
        if response.status_code == 200:
            resp_json = response.json()
            return resp_json.get('access_token'), resp_json.get('open_id')
        return None, None
    except:
        return None, None

def major_login(access_token, open_id, region='IND'):
    region_config = REGION_CONFIG.get(region, REGION_CONFIG['IND'])
    url = region_config['major_login_url']
    
    payload_template = bytes.fromhex(
        '1a13323032352d30372d33302031313a30323a3531220966726565206669726528013a07312e3132302e32422c416e64726f6964204f5320372e312e32202f204150492d323320284e32473438482f373030323530323234294a0848616e6468656c645207416e64726f69645a045749464960c00c68840772033332307a1f41524d7637205646507633204e454f4e20564d48207c2032343635207c203480019a1b8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e319a012b476f6f676c657c31663361643662372d636562342d343934622d383730622d623164616364373230393131a2010c3139372e312e31322e313335aa0102656eb201203939366136323964626364623339363462653662363937386635643831346462ba010134c2010848616e6468656c64ea014066663930633037656239383135616633306134336234613966363031393531366530653463373033623434303932353136643064656661346365663531663261f00101ca0207416e64726f6964d2020457494649ca03203734323862323533646566633136343031386336303461316562626665626466e003daa907e803899b07f003bf0ff803ae088004999b078804daa9079004999b079804daa907c80403d204262f646174612f6170702f636f6d2e6474732e667265656669726574682d312f6c69622f61726de00401ea044832303837663631633139663537663261663465376665666630623234643964397c2f646174612f6170702f636f6d2e6474732e667265656669726574682d312f626173652e61706bf00403f804018a050233329a050a32303139313138363933b205094f70656e474c455332b805ff7fc00504e005dac901ea0507616e64726f6964f2055c4b71734854394748625876574c6668437950416c52526873626d43676542557562555551317375746d525536634e30524f3751453141486e496474385963784d614c575437636d4851322b7374745279377830663935542b6456593d8806019006019a060134a2060134'
    )
    OLD_OPEN_ID = b"996a629dbcdb3964be6b6978f5d814db"
    OLD_ACCESS_TOKEN = b"ff90c07eb9815af30a43b4a9f6019516e0e4c703b44092516d0defa4cef51f2a"
    
    payload = payload_template.replace(OLD_OPEN_ID, open_id.encode())
    payload = payload.replace(OLD_ACCESS_TOKEN, access_token.encode())
    
    encrypted = encrypt_api(payload.hex())
    if not encrypted:
        return None
    
    headers = {
        'X-Unity-Version': '2018.4.11f1',
        'ReleaseVersion': 'OB53',
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-GA': 'v1 1',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
        'Host': 'loginbp.ggblueshark.com',
        'Connection': 'Keep-Alive',
    }
    
    try:
        response = requests.post(url, headers=headers, data=bytes.fromhex(encrypted), timeout=30, verify=False)
        if response.status_code == 200 and len(response.content) > 0:
            return response.content
        return None
    except:
        return None

def parse_major_login_response(serialized_data):
    try:
        major_log_res = MajorLoginRes_pb2.MajorLoginRes()
        major_log_res.ParseFromString(serialized_data)
        return getattr(major_log_res, 'token', None)
    except:
        return None

def create_account(region, name_prefix):
    password = generate_password()
    account_name = generate_random_name(name_prefix)
    
    # Step 1: Register guest
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
    
    # Step 2: Get token
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
    
    # Step 3: MajorRegister
    encoded_field = encode_string(open_id)
    field_escaped = to_unicode_escaped(encoded_field)
    field_bytes = field_escaped.encode('latin1')
    
    lang_code = REGION_LANG.get(region, "en")
    proto_payload = {1: account_name, 2: access_token, 3: open_id, 5: 102000007, 6: 4, 7: 1, 13: 1, 14: field_bytes, 15: lang_code, 16: 1, 17: 1}
    
    proto_bytes = create_proto(proto_payload)
    encrypted_reg = e_aes(proto_bytes.hex())
    
    register_url = "https://loginbp.ggblueshark.com/MajorRegister"
    if region in ["ME", "TH"]:
        register_url = "https://loginbp.common.ggbluefox.com/MajorRegister"
    
    reg_headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
        "Content-Type": "application/x-www-form-urlencoded",
        "ReleaseVersion": "OB53",
        "X-Unity-Version": "2018.4."
    }
    requests.post(register_url, headers=reg_headers, data=encrypted_reg, timeout=30, verify=False)
    time.sleep(random.uniform(0.3, 0.7))
    
    # Step 4: MajorLogin to get account ID
    major_resp = major_login(access_token, open_id, region)
    if not major_resp:
        raise Exception("MajorLogin failed")
    
    jwt_token = parse_major_login_response(major_resp)
    if not jwt_token:
        raise Exception("JWT extraction failed")
    
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
        from urllib.parse import urlparse, parse_qs
        
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        name = params.get('name', ['TutorSensi'])[0][:9]
        amount = params.get('amount', ['1'])[0]
        server = params.get('server', ['ind'])[0]
        
        try:
            count = min(max(1, int(amount)), 10)
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
                time.sleep(0.3)
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
