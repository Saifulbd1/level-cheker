import os
import re
import json
import time
import uuid
import shutil
import base64
import threading

import httpx
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from Crypto.Cipher import AES

from google.protobuf import json_format
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
from google.protobuf.message import Message
import main_pb2
import AccountPersonalShow_pb2


# ============================================================
#  PART 1 — FreeFire_pb2 (inlined)
# ============================================================

_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0e\x46reeFire.proto"c\n\x08LoginReq\x12\x0f\n\x07open_id\x18\x16 \x01(\t'
    b'\x12\x14\n\x0copen_id_type\x18\x17 \x01(\t\x12\x13\n\x0blogin_token\x18\x1d '
    b'\x01(\t\x12\x1b\n\x13orign_platform_type\x18\x63 \x01(\t"]\n\x10\x42lacklist'
    b'InfoRes\x12\x1e\n\nban_reason\x18\x01 \x01(\x0e\x32\n.BanReason\x12\x17\n'
    b'\x0f\x65xpire_duration\x18\x02 \x01(\r\x12\x10\n\x08\x62\x61n_time\x18\x03 '
    b'\x01(\r"f\n\x0eLoginQueueInfo\x12\r\n\x05\x61llow\x18\x01 \x01(\x08\x12'
    b'\x16\n\x0equeue_position\x18\x02 \x01(\r\x12\x16\n\x0eneed_wait_secs\x18'
    b'\x03 \x01(\r\x12\x15\n\rqueue_is_full\x18\x04 \x01(\x08"\xa0\x03\n\x08'
    b'LoginRes\x12\x12\n\naccount_id\x18\x01 \x01(\x04\x12\x13\n\x0block_region'
    b'\x18\x02 \x01(\t\x12\x13\n\x0bnoti_region\x18\x03 \x01(\t\x12\x11\n\tip_'
    b'region\x18\x04 \x01(\t\x12\x19\n\x11\x61gora_environment\x18\x05 \x01(\t'
    b'\x12\x19\n\x11new_active_region\x18\x06 \x01(\t\x12\x19\n\x11recommend_'
    b'regions\x18\x07 \x03(\t\x12\r\n\x05token\x18\x08 \x01(\t\x12\x0b\n\x03ttl'
    b'\x18\t \x01(\r\x12\x12\n\nserver_url\x18\n \x01(\t\x12\x16\n\x0e\x65mul'
    b'ator_score\x18\x0b \x01(\r\x12$\n\tblacklist\x18\x0c \x01(\x0b\x32\x11.'
    b'BlacklistInfoRes\x12#\n\nqueue_info\x18\r \x01(\x0b\x32\x0f.LoginQueue'
    b'Info\x12\x0e\n\x06tp_url\x18\x0e \x01(\t\x12\x15\n\rapp_server_id\x18'
    b'\x0f \x01(\r\x12\x0f\n\x07\x61no_url\x18\x10 \x01(\t\x12\x0f\n\x07ip_city'
    b'\x18\x11 \x01(\t\x12\x16\n\x0eip_subdivision\x18\x12 \x01(\t*\xa8\x01\n'
    b'\tBanReason\x12\x16\n\x12\x42\x41N_REASON_UNKNOWN\x10\x00\x12\x1b\n\x17'
    b'\x42\x41N_REASON_IN_GAME_AUTO\x10\x01\x12\x15\n\x11\x42\x41N_REASON_'
    b'REFUND\x10\x02\x12\x15\n\x11\x42\x41N_REASON_OTHERS\x10\x03\x12\x16\n'
    b'\x12\x42\x41N_REASON_SKINMOD\x10\x04\x12 \n\x1b\x42\x41N_REASON_IN_GAME'
    b'_AUTO_NEW\x10\xf6\x07\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "FreeFire_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_BANREASON"]._serialized_start = 738
    _globals["_BANREASON"]._serialized_end = 906
    _globals["_LOGINREQ"]._serialized_start = 18
    _globals["_LOGINREQ"]._serialized_end = 117
    _globals["_BLACKLISTINFORES"]._serialized_start = 119
    _globals["_BLACKLISTINFORES"]._serialized_end = 212
    _globals["_LOGINQUEUEINFO"]._serialized_start = 214
    _globals["_LOGINQUEUEINFO"]._serialized_end = 316
    _globals["_LOGINRES"]._serialized_start = 319
    _globals["_LOGINRES"]._serialized_end = 735

LoginReq = _globals["LoginReq"]
LoginRes = _globals["LoginRes"]


# ============================================================
#  PART 2 — Settings
# ============================================================

MAIN_KEY = base64.b64decode("WWcmdGMlREV1aDYlWmNeOA==")
MAIN_IV = base64.b64decode("Nm95WkRyMjJFM3ljaGpNJQ==")

# Env override সাপোর্ট — নতুন OB version এলে restart ছাড়াই update করা যাবে
RELEASEVERSION = os.environ.get("FF_RELEASE_VERSION", "OB55")
USERAGENT = "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)"
LOGIN_URL = os.environ.get("FF_LOGIN_URL", "https://loginbp.ppmainecoonghj.com/")

# Garena guest OAuth — env দিয়ে override করা যাবে (নতুন secret পেলে)
GUEST_CLIENT_ID     = os.environ.get("FF_CLIENT_ID", "100067")
GUEST_CLIENT_SECRET = os.environ.get(
    "FF_CLIENT_SECRET",
    "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
)

# Rate limit — Garena OAuth এর জন্য নিরাপদ দূরত্ব
REQUEST_DELAY_SEC = float(os.environ.get("FF_REQUEST_DELAY", "1.2"))
MAX_RETRIES = int(os.environ.get("FF_MAX_RETRIES", "2"))

HTTP_LIMITS = httpx.Limits(max_keepalive_connections=20, max_connections=50)
HTTP_TIMEOUT = httpx.Timeout(20.0, connect=6.0)
_http_client = httpx.Client(limits=HTTP_LIMITS, timeout=HTTP_TIMEOUT)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

GUEST_DIR = os.path.join(BASE_DIR, "GUEST")
VALID_DIR = os.path.join(GUEST_DIR, "VALID")
INVALID_DIR = os.path.join(GUEST_DIR, "INVALID")
INVALID_FILE = os.path.join(INVALID_DIR, "invalid.json")

os.makedirs(VALID_DIR, exist_ok=True)
os.makedirs(INVALID_DIR, exist_ok=True)
if not os.path.exists(INVALID_FILE):
    with open(INVALID_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, indent=2, ensure_ascii=False)

app = Flask(__name__)
CORS(app)


# ============================================================
#  PART 3 — Helpers (AES / proto / login)
# ============================================================

class LoginError(Exception):
    """Login pipeline এর specific stage error।"""
    def __init__(self, stage, msg):
        self.stage = stage
        self.msg = msg
        super().__init__(f"[{stage}] {msg}")


def pad(text: bytes) -> bytes:
    padding_length = AES.block_size - (len(text) % AES.block_size)
    return text + bytes([padding_length] * padding_length)


def aes_cbc_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    return AES.new(key, AES.MODE_CBC, iv).encrypt(pad(plaintext))


def json_to_proto(json_data: str, proto_message: Message) -> bytes:
    json_format.ParseDict(json.loads(json_data), proto_message)
    return proto_message.SerializeToString()


def try_parse_login_res(data: bytes):
    try:
        msg = LoginRes()
        msg.ParseFromString(data)
        if msg.account_id and msg.account_id > 0:
            return json.loads(json_format.MessageToJson(msg))
    except Exception:
        pass
    return None


def extract_login_res(raw: bytes) -> dict:
    parsed = try_parse_login_res(raw)
    if parsed:
        return parsed

    idx = 0
    while True:
        idx = raw.find(b"\x08", idx)
        if idx == -1:
            break
        parsed = try_parse_login_res(raw[idx:])
        if parsed:
            return parsed
        idx += 1

    jwt_marker = raw.find(b"eyJhbGciOiJIUzI1NiIs")
    if jwt_marker != -1:
        for i in range(jwt_marker - 1, max(jwt_marker - 300, -1), -1):
            if raw[i] == 0x42:
                parsed = try_parse_login_res(raw[i:])
                if parsed:
                    return parsed
                break

    raise LoginError(
        "MajorLogin",
        f"LoginRes parse failed (bytes={len(raw)}): {raw[:120]!r}"
    )


# ---------- FIX #1: get_access_token with diagnostic ----------

def get_access_token(account: str):
    """
    Returns (access_token, open_id).
    Raises LoginError with clear stage/message on failure.
    """
    url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
    payload = (
        account
        + "&response_type=token&client_type=2"
        + f"&client_secret={GUEST_CLIENT_SECRET}"
        + f"&client_id={GUEST_CLIENT_ID}"
    )
    headers = {
        "User-Agent": USERAGENT,
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    last_err = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = _http_client.post(url, data=payload, headers=headers)
            break
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout) as e:
            last_err = e
            time.sleep(1.0 * (attempt + 1))
    else:
        raise LoginError("OAuth", f"Network error: {last_err}")

    if resp.status_code != 200:
        raise LoginError(
            "OAuth",
            f"HTTP {resp.status_code} from Garena OAuth: {resp.text[:200]!r}"
        )

    # Response parse — JSON না হলে raw দেখাও
    try:
        data = resp.json()
    except Exception:
        raise LoginError("OAuth", f"Non-JSON OAuth response: {resp.text[:200]!r}")

    # Standard format
    token = data.get("access_token") or data.get("token") or "0"
    open_id = data.get("open_id") or data.get("uid") or "0"

    # Garena sometimes returns error object
    if token == "0" or open_id == "0":
        err_code = data.get("error") or data.get("error_code") or "no_token"
        err_desc = data.get("error_description") or data.get("message") or ""
        raise LoginError(
            "OAuth",
            f"Garena rejected credentials (code={err_code} {err_desc}) — "
            f"uid={account.split('&')[0]}. "
            f"Possible: wrong password / banned / region-locked / client_secret outdated"
        )

    return token, open_id


def generate_jwt_token(uid: str, password: str):
    start_time = time.time()

    # Stage 1: Garena guest OAuth
    token_val, open_id = get_access_token(f"uid={uid}&password={password}")

    # Stage 2: MajorLogin (build encrypted proto)
    body = json.dumps({
        "open_id": open_id,
        "open_id_type": "4",
        "login_token": token_val,
        "orign_platform_type": "4",
    })
    proto_bytes = json_to_proto(body, LoginReq())
    payload = aes_cbc_encrypt(MAIN_KEY, MAIN_IV, proto_bytes)

    headers = {
        "User-Agent": USERAGENT,
        "Accept": "*/*",
        "Accept-Encoding": "deflate, gzip",
        "X-Ga-Sv": "1789534056",
        "Authorization": "Bearer",
        "X-Ga": "v1 1",
        "Releaseversion": RELEASEVERSION,
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Unity-Version": "2018.4.12f1",
        "PlAy_VeR": "1.132.1",
        "Ob_VeR": RELEASEVERSION,
    }

    last_err = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = _http_client.post(
                f"{LOGIN_URL}MajorLogin", data=payload, headers=headers
            )
            break
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout) as e:
            last_err = e
            time.sleep(1.0 * (attempt + 1))
    else:
        raise LoginError("MajorLogin", f"Network error: {last_err}")

    if resp.status_code != 200:
        raise LoginError(
            "MajorLogin",
            f"HTTP {resp.status_code} from login server: {resp.text[:200]!r}"
        )

    msg = extract_login_res(resp.content)

    elapsed = time.time() - start_time

    return {
        "access_token": token_val,
        "open_id": open_id,
        "real_uid": str(msg.get("accountId", "")),
        "status": "success",
        "time": f"{elapsed:.2f}s",
        "token": f"{msg.get('token', '')}",
        "region": msg.get("lockRegion", ""),
        "server_url": msg.get("serverUrl", ""),
    }


def get_account_information(uid, login_data):
    token = login_data.get("token", "")
    server_url = login_data.get("server_url", "")
    region = login_data.get("region", "") or "N/A"
    if not token or not server_url:
        raise LoginError("AccountInfo", "Login response missing token/serverUrl")

    payload = json.dumps({"a": int(uid), "b": "7"})
    proto = main_pb2.GetPlayerPersonalShow()
    json_format.ParseDict(json.loads(payload), proto)
    proto_bytes = proto.SerializeToString()
    encrypted = aes_cbc_encrypt(MAIN_KEY, MAIN_IV, proto_bytes)

    headers = {
        "User-Agent": USERAGENT,
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/octet-stream",
        "Authorization": token if token.startswith("Bearer ") else f"Bearer {token}",
        "X-Unity-Version": "2018.4.12f1",
        "X-GA": "v1 1",
        "ReleaseVersion": RELEASEVERSION,
    }

    resp = _http_client.post(
        server_url.rstrip("/") + "/GetPlayerPersonalShow",
        data=encrypted,
        headers=headers,
    )
    if resp.status_code != 200:
        raise LoginError(
            "AccountInfo",
            f"HTTP {resp.status_code} from game server: {resp.text[:200]!r}"
        )

    msg = AccountPersonalShow_pb2.AccountPersonalShowInfo()
    msg.ParseFromString(resp.content)
    data = json.loads(json_format.MessageToJson(msg))

    basic = data.get("basicInfo", {})

    return {
        "status": "success",
        "raw_region": basic.get("region", region),
        "BasicInformation": {
            "Name": basic.get("nickname", "Unknown"),
            "UID": str(uid),
            "Level": basic.get("level", 0) or 0,
            "Region": basic.get("region", region),
            "Password": str(login_data.get("_password", "")),
        },
    }


# ============================================================
#  PART 4 — STORAGE SYSTEM
# ============================================================

_lock = threading.Lock()

BATCH_STATE = {
    "files": [],
    "queue": [],
    "running": False,
}


def safe_region(region):
    r = str(region or "").strip().upper()
    if not r or r in ("N/A", "NONE"):
        r = "UNKNOWN"
    return re.sub(r"[^A-Za-z0-9_-]", "_", r)


def _load_json_list(path):
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_json_list(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def save_valid_account(account_uid, main_uid, main_password, name, level, server):
    server = safe_region(server)
    try:
        level = int(level or 0)
    except Exception:
        level = 0

    record = {
        "account_uid": str(account_uid),
        "name": str(name) if name else "Unknown",
        "level": level,
        "server": server,
        "main_uid": str(main_uid),
        "main_password": str(main_password),
    }

    server_dir = os.path.join(VALID_DIR, server)
    os.makedirs(server_dir, exist_ok=True)

    fname = f"{level}_LEVEL----{server}.json"
    lvl_path = os.path.join(server_dir, fname)

    with _lock:
        existing = _load_json_list(lvl_path)
        for a in existing:
            if str(a.get("account_uid")) == record["account_uid"]:
                return lvl_path
        existing.append(record)
        _save_json_list(lvl_path, existing)

    return lvl_path


# ---------- FIX #2: invalid record includes stage ----------

def save_invalid_account(account_uid, main_uid, main_password, error):
    # LoginError হলে stage আলাদা করি
    stage = "Unknown"
    err_text = str(error)
    if isinstance(error, LoginError):
        stage = error.stage
        err_text = error.msg

    record = {
        "account_uid": str(account_uid),
        "main_uid": str(main_uid),
        "main_password": str(main_password),
        "stage": stage,
        "error": err_text[:400],
        "checked_at": time.strftime("%d %b %Y %H:%M:%S"),
    }

    with _lock:
        os.makedirs(INVALID_DIR, exist_ok=True)
        existing = _load_json_list(INVALID_FILE)
        for a in existing:
            if str(a.get("account_uid")) == record["account_uid"]:
                return INVALID_FILE
        existing.append(record)
        _save_json_list(INVALID_FILE, existing)

    return INVALID_FILE


# ---------- FIX #3: rate-limit delay in worker ----------

def batch_worker():
    while True:
        with _lock:
            if not BATCH_STATE["queue"]:
                BATCH_STATE["running"] = False
                return
            file_id, uid, password, main_uid, main_password = BATCH_STATE["queue"].pop(0)

        fstate = None
        with _lock:
            for f in BATCH_STATE["files"]:
                if f["id"] == file_id:
                    fstate = f
                    break
        if fstate is None:
            continue

        try:
            login = generate_jwt_token(str(uid), str(password))
            real_uid = login.get("real_uid") or uid

            name = "Unknown"
            level = 0
            region = login.get("region") or "UNKNOWN"
            try:
                login["_password"] = password
                info = get_account_information(real_uid, login)
                basic = info.get("BasicInformation", {})
                name = basic.get("Name", "Unknown")
                level = basic.get("Level", 0) or 0
                region = basic.get("Region") or region
            except Exception as e:
                # account valid কিন্তু profile fetch fail — তবু valid হিসেবে save
                print(f"[WARN] AccountInfo failed for {real_uid}: {e}")

            save_valid_account(real_uid, main_uid, main_password, name, level, region)

            with _lock:
                fstate["valid"] += 1
        except Exception as e:
            save_invalid_account(uid, main_uid, main_password, e)
            with _lock:
                fstate["invalid"] += 1
        finally:
            with _lock:
                fstate["done"] += 1
            # Rate limit — Garena OAuth block এড়াতে
            time.sleep(REQUEST_DELAY_SEC)


def start_worker_if_needed():
    with _lock:
        already = BATCH_STATE["running"]
        BATCH_STATE["running"] = True
    if not already:
        threading.Thread(target=batch_worker, daemon=True).start()


def build_summary():
    servers = {}
    if not os.path.isdir(VALID_DIR):
        return servers
    for r in sorted(os.listdir(VALID_DIR)):
        rpath = os.path.join(VALID_DIR, r)
        if not os.path.isdir(rpath):
            continue
        levels = []
        total = 0
        for fn in sorted(os.listdir(rpath)):
            if not fn.endswith(".json"):
                continue
            m = re.match(r"^(\d+)_LEVEL----", fn)
            lvl = int(m.group(1)) if m else fn[:-5]
            cnt = len(_load_json_list(os.path.join(rpath, fn)))
            levels.append({"level": lvl, "file": fn, "count": cnt})
            total += cnt
        if total > 0:
            servers[r] = {"total": total, "levels": levels}
    return servers


def get_invalid_list():
    return _load_json_list(INVALID_FILE)


# ============================================================
#  PART 5 — Routes
# ============================================================

@app.route("/")
def index():
    return """
<!doctype html><html lang="bn"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>VOID — GUEST Account Organizer</title>
<style>
:root{
--bg:#070b15;--bg2:#0b1220;--card:rgba(17,24,39,.72);--border:#1e293b;--border2:#334155;
--text:#e5e7eb;--muted:#8b9bb4;--green:#4ade80;--red:#f87171;--blue:#60a5fa;
--gold:#fbbf24;--accent:#7c3aed;--accent2:#2563eb;--shadow:0 20px 60px rgba(0,0,0,.5)
}
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
body{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,-apple-system,sans-serif;min-height:100vh;overflow-x:hidden}
body::before{content:'';position:fixed;inset:0;z-index:-1;
background:radial-gradient(700px 400px at 15% -5%,rgba(124,58,237,.18),transparent),
radial-gradient(600px 380px at 95% 10%,rgba(37,99,235,.14),transparent),
radial-gradient(500px 300px at 50% 110%,rgba(16,185,129,.10),transparent)}
.wrap{max-width:820px;margin:0 auto;padding:18px 14px 60px}
header{display:flex;align-items:center;gap:12px;padding:8px 4px 18px}
.logo{width:48px;height:48px;border-radius:14px;display:grid;place-items:center;font-size:24px;
background:linear-gradient(135deg,var(--accent),var(--accent2));box-shadow:0 8px 24px rgba(124,58,237,.4)}
header h1{font-size:20px;letter-spacing:.5px;background:linear-gradient(90deg,#fff,#a5b4fc);
-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
header .sub{font-size:11px;color:var(--muted);margin-top:2px}
.card{background:var(--card);border:1px solid var(--border);border-radius:20px;padding:20px;
margin-bottom:16px;box-shadow:var(--shadow);backdrop-filter:blur(14px)}
.card h2{font-size:15px;display:flex;align-items:center;gap:8px;margin-bottom:6px}
.card h2 .tag{font-size:10px;font-weight:600;color:var(--blue);background:rgba(96,165,250,.12);
border:1px solid rgba(96,165,250,.25);padding:2px 8px;border-radius:20px}
.muted{color:var(--muted);font-size:12px;line-height:1.6}
label{display:block;margin:14px 0 6px;font-size:12px;color:var(--muted);font-weight:600}
.dz{border:2px dashed var(--border2);border-radius:14px;padding:18px 12px;text-align:center;
color:var(--muted);font-size:13px;cursor:pointer;transition:.25s;background:rgba(2,6,23,.35)}
.dz:active,.dz.on{border-color:var(--accent);color:var(--blue);background:rgba(124,58,237,.08)}
.dz .files{margin-top:8px;display:flex;flex-wrap:wrap;gap:6px;justify-content:center}
.chip{font-size:11px;background:rgba(74,222,128,.12);color:var(--green);
border:1px solid rgba(74,222,128,.3);padding:3px 10px;border-radius:20px}
button{margin-top:14px;width:100%;padding:14px;border:0;border-radius:14px;font-size:14px;font-weight:700;
color:#fff;cursor:pointer;transition:.2s;position:relative;overflow:hidden}
button.primary{background:linear-gradient(135deg,var(--accent),var(--accent2));box-shadow:0 8px 24px rgba(124,58,237,.35)}
button.primary:active{transform:scale(.98)}
button.danger{background:rgba(220,38,38,.15);color:var(--red);border:1px solid rgba(220,38,38,.4)}
button:disabled{opacity:.55;cursor:not-allowed}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:0}
.stat{background:rgba(2,6,23,.5);border:1px solid var(--border);border-radius:16px;padding:14px 8px;text-align:center}
.stat .n{font-size:24px;font-weight:800;line-height:1.1}
.stat .lbl{font-size:10px;color:var(--muted);margin-top:4px;text-transform:uppercase;letter-spacing:.5px}
.sv{color:var(--green)}.in{color:var(--red)}.tt{color:var(--blue)}
.fstat{background:rgba(2,6,23,.45);border:1px solid var(--border);border-radius:14px;padding:12px;margin:10px 0}
.fstat .top{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:8px;font-size:12px}
.pill{font-size:10px;font-weight:700;padding:2px 10px;border-radius:20px}
.pill.run{color:var(--gold);background:rgba(251,191,36,.12);border:1px solid rgba(251,191,36,.35)}
.pill.done{color:var(--green);background:rgba(74,222,128,.12);border:1px solid rgba(74,222,128,.35)}
.bar{height:10px;background:#020617;border-radius:8px;overflow:hidden}
.bar>div{height:100%;width:0%;border-radius:8px;transition:.4s;
background:linear-gradient(90deg,var(--accent),#22d3ee);background-size:200% 100%;animation:flow 2s linear infinite}
@keyframes flow{to{background-position:200% 0}}
.fstat .nums{font-size:11px;color:var(--muted);margin-top:6px}
.rg{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.rgc{background:rgba(2,6,23,.45);border:1px solid var(--border);border-radius:16px;padding:14px;cursor:pointer;transition:.2s;position:relative;overflow:hidden}
.rgc:active{transform:scale(.97)}
.rgc h3{font-size:15px;display:flex;align-items:center;gap:6px}
.rgc h3 .flag{width:11px;height:11px;border-radius:3px;background:linear-gradient(135deg,var(--accent),var(--accent2))}
.rgc .cnt{font-size:22px;font-weight:800;color:var(--green);margin:6px 0 2px}
.lvlbox{display:none}
.lvrow{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid var(--border);font-size:13px}
.lvrow:last-child{border-bottom:0}
.lvrow b{color:var(--gold)}
a.dl{color:var(--blue);text-decoration:none;font-size:11px;font-weight:700;border:1px solid rgba(96,165,250,.4);
padding:5px 12px;border-radius:20px;white-space:nowrap;transition:.2s}
a.dl:active{background:rgba(96,165,250,.15)}
.scrollbox{max-height:260px;overflow:auto;background:rgba(2,6,23,.55);border:1px solid var(--border);
border-radius:14px;padding:12px;font-size:11px;font-family:ui-monospace,Consolas,monospace;white-space:pre-wrap;word-break:break-all}
.scrollbox::-webkit-scrollbar{width:5px}.scrollbox::-webkit-scrollbar-thumb{background:var(--border2);border-radius:4px}
.back{color:var(--blue);text-decoration:none;font-size:12px;cursor:pointer;display:inline-block;margin-top:10px}
.empty{text-align:center;padding:18px;font-size:12px;color:var(--muted)}
.progressbar{height:5px;background:#020617;border-radius:4px;overflow:hidden;margin:14px 0 4px}
.progressbar>div{height:100%;width:0%;background:linear-gradient(90deg,var(--accent),#22d3ee);transition:.4s}
.prc{display:flex;justify-content:space-between;font-size:10px;color:var(--muted);margin-bottom:8px}
@media(max-width:480px){
.wrap{padding:12px 10px 40px}.card{padding:16px;border-radius:16px}
header h1{font-size:17px}.logo{width:42px;height:42px;font-size:20px}
.stat .n{font-size:20px}.rg{grid-template-columns:repeat(2,1fr)}
}
</style></head><body><div class="wrap">

<header><div class="logo">👹</div>
<div><h1>VOID — GUEST ORGANIZER</h1>
<div class="sub">GUEST/VALID/&lt;SERVER&gt;/LEVEL JSON • GUEST/INVALID/invalid.json</div></div></header>

<div class="card">
<h2>📤 Upload JSON <span class="tag">MAX 3</span></h2>
<div class="muted">JSON ফাইল সিলেক্ট করুন (uid + password list) → ব্যাচ চেক শুরু হবে → সব রেজাল্ট অটো-সেভ হবে।</div>
<form id="upform">
<div class="dz" id="dz">
<div id="dz-label">📄 ট্যাপ করে JSON ফাইল সিলেক্ট করুন (১-৩টি)</div>
<div class="files" id="dz-files"></div>
<input type="file" id="fpick" accept=".json,application/json" multiple hidden>
</div>
<button class="primary" id="upbtn" type="submit">🚀 Upload &amp; Start Batch</button>
</form>
<div class="progressbar"><div id="gbar"></div></div>
<div class="prc"><span id="gpc">0%</span><span id="gdone">0 / 0</span></div>
</div>

<div class="card"><h2>📊 Live Stats</h2>
<div class="stats">
<div class="stat"><div class="n tt" id="t-total">0</div><div class="lbl">Total IDs</div></div>
<div class="stat"><div class="n sv" id="t-valid">0</div><div class="lbl">Valid ✅</div></div>
<div class="stat"><div class="n in" id="t-invalid">0</div><div class="lbl">Invalid ❌</div></div>
</div>
<div id="files" class="empty">এখনো কোনো ফাইল আপলোড হয়নি...</div></div>

<div class="card"><h2>🌍 Servers <span class="tag">GUEST/VALID</span></h2>
<div id="regions" class="rg"><div class="empty">Loading...</div></div></div>

<div class="card lvlbox" id="levelcard">
<h2 id="lv-title">📁 Levels</h2><a class="back" onclick="hideLv()">← hide</a>
<div id="lv-body" style="margin-top:8px"></div></div>

<div class="card"><h2>❌ Invalid Accounts <span class="tag">invalid.json</span></h2>
<div class="scrollbox" id="invalid">Loading...</div>
<div style="display:flex;gap:10px">
<button class="danger" id="resetbtn" type="button">🗑 Reset All</button>
<button class="primary" id="dlbtn" type="button" style="margin-top:14px">⬇ Download invalid.json</button>
</div></div>

</div><script>
function esc(x){return String(x??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]))}
let timer=null;

const dz=document.getElementById('dz'),fpick=document.getElementById('fpick');
dz.addEventListener('click',()=>fpick.click());
fpick.addEventListener('change',renderChips);
['dragover','dragenter'].forEach(ev=>dz.addEventListener(ev,e=>{e.preventDefault();dz.classList.add('on')}));
['dragleave','drop'].forEach(ev=>dz.addEventListener(ev,e=>{e.preventDefault();dz.classList.remove('on')}));
dz.addEventListener('drop',e=>{fpick.files=e.dataTransfer.files;renderChips()});
function renderChips(){const el=document.getElementById('dz-files');let h='';
[...fpick.files].forEach(f=>{h+='<span class="chip">'+esc(f.name)+'</span>'});
el.innerHTML=h;
document.getElementById('dz-label').textContent=fpick.files.length?fpick.files.length+' file(s) selected — ready to start':'📄 ট্যাপ করে JSON ফাইল সিলেক্ট করুন (১-৩টি)'}

document.getElementById('upform').addEventListener('submit',async e=>{
 e.preventDefault();const btn=document.getElementById('upbtn');
 const files=[...fpick.files].slice(0,3);
 if(!files.length){alert('অন্তত একটা JSON ফাইল দিন!');return}
 btn.disabled=true;btn.textContent='⏳ Uploading...';
 const fd=new FormData();files.forEach(f=>fd.append('files',f));
 try{const r=await fetch('/batch/upload',{method:'POST',body:fd});const d=await r.json();
  if(d.status!=='success'){alert(d.error||'Failed')}
  else if(!timer){timer=setInterval(loadStatus,2000)}
 }catch(err){alert(err)}
 btn.disabled=false;btn.textContent='🚀 Upload & Start Batch';loadStatus()});

document.getElementById('resetbtn').addEventListener('click',async()=>{
 if(!confirm('GUEST ফোল্ডারের সব valid/invalid ডাটা ও progress মুছে যাবে! নিশ্চিত?'))return;
 await fetch('/reset',{method:'POST'});
 if(timer){clearInterval(timer);timer=null}loadStatus()});

document.getElementById('dlbtn').addEventListener('click',()=>window.location.href='/invalid/download');

async function loadStatus(){
 try{const r=await fetch('/batch/status');const d=await r.json();
 const fb=document.getElementById('files');
 if(!d.files.length){fb.innerHTML='<div class="empty">এখনো কোনো ফাইল আপলোড হয়নি...</div>'}
 else{let h='';let T=0,D=0;
  d.files.forEach(f=>{T+=f.total;D+=f.done;const p=f.total?Math.round(f.done/f.total*100):0;
  h+='<div class="fstat"><div class="top"><b>'+esc(f.name)+'</b>'+
  (f.total>0&&f.done>=f.total?'<span class="pill done">✅ COMPLETE</span>':'<span class="pill run">⏳ '+p+'%</span>')+'</div>'+
  '<div class="bar"><div style="width:'+p+'%"></div></div>'+
  '<div class="nums">Found: '+f.total+' • Done: '+f.done+' • ✅ <b class="sv">'+f.valid+'</b> • ❌ <b class="in">'+f.invalid+'</b></div></div>'});
  fb.innerHTML=h;
  const gp=T?Math.round(D/T*100):0;
  document.getElementById('gbar').style.width=gp+'%';
  document.getElementById('gpc').textContent=gp+'%';
  document.getElementById('gdone').textContent=D+' / '+T;}
 document.getElementById('t-total').textContent=d.totals.total;
 document.getElementById('t-valid').textContent=d.totals.valid;
 document.getElementById('t-invalid').textContent=d.totals.invalid;
 renderRegions(d.regions);
 document.getElementById('invalid').textContent=d.invalid_list.length?
  JSON.stringify(d.invalid_list,null,2):'— কোনো invalid account নেই —';
 if(!d.running&&timer){clearInterval(timer);timer=null}
 }catch(e){}}

function renderRegions(regions){
 const el=document.getElementById('regions');const keys=Object.keys(regions||{});
 if(!keys.length){el.innerHTML='<div class="empty">এখনো কোনো valid server ডাটা নেই...</div>';return}
 let h='';for(const k of keys){
 h+='<div class="rgc" onclick="openRegion(\\''+k+'\\')"><h3><span class="flag"></span>'+esc(k)+'</h3>'+
 '<div class="cnt">'+regions[k].total+' IDs ✅</div><div class="muted" style="font-size:10px">'+regions[k].levels.length+' level files</div></div>'}
 el.innerHTML=h}

async function openRegion(r){
 const res=await fetch('/region/'+encodeURIComponent(r));const d=await res.json();
 const card=document.getElementById('levelcard');card.style.display='block';
 document.getElementById('lv-title').innerHTML='📁 '+esc(r)+' — Level Breakdown <span class="tag">GUEST/VALID/'+esc(r)+'</span>';
 let h='';(d.levels||[]).forEach(l=>{
 h+='<div class="lvrow"><span>⚡ Level <b>'+esc(l.level)+'</b> — '+l.count+' IDs <span class="muted">('+esc(l.file)+')</span></span>'+
 '<a class="dl" href="/file/'+encodeURIComponent(r)+'/'+encodeURIComponent(l.file)+'" download>⬇</a></div>'});
 document.getElementById('lv-body').innerHTML=h;card.scrollIntoView({behavior:'smooth'})}
function hideLv(){document.getElementById('levelcard').style.display='none'}

loadStatus();timer=setInterval(loadStatus,2000);
</script></body></html>"""


@app.route("/batch/upload", methods=["POST"])
def batch_upload():
    files = [f for f in request.files.getlist("files") if f and f.filename]
    if not files:
        return jsonify({"status": "error", "error": "কোনো ফাইল পাওয়া যায়নি"}), 400
    if len(files) > 3:
        return jsonify({"status": "error", "error": "সর্বোচ্চ ৩টা JSON ফাইল একসাথে দেওয়া যাবে"}), 400

    queued = 0
    for f in files:
        try:
            raw = f.read()
            entries = json.loads(raw.decode("utf-8", errors="ignore"))
        except Exception:
            return jsonify({"status": "error", "error": f"{f.filename} পার্স করা যায়নি — valid JSON দিন"}), 400

        if isinstance(entries, dict):
            entries = entries.get("accounts") or entries.get("data") or []

        # ---------- FIX #1: main_uid / main_password support ----------
        clean = []
        seen = set()
        for e in entries:
            if not isinstance(e, dict):
                continue
            uid = str(e.get("uid", "")).strip()
            pw = str(e.get("password", ""))
            if not uid or not pw or uid in seen:
                continue
            seen.add(uid)
            # JSON-এ main_uid/main_password থাকলে সেটা, নাহলে guest নিজেই main
            main_uid = str(e.get("main_uid", uid)).strip() or uid
            main_pw = str(e.get("main_password", pw)) or pw
            clean.append((uid, pw, main_uid, main_pw))

        file_state = {
            "id": str(uuid.uuid4()),
            "name": f.filename,
            "total": len(clean),
            "done": 0,
            "valid": 0,
            "invalid": 0,
        }
        with _lock:
            BATCH_STATE["files"].append(file_state)
            for uid, pw, main_uid, main_pw in clean:
                BATCH_STATE["queue"].append(
                    (file_state["id"], uid, pw, main_uid, main_pw)
                )
        queued += len(clean)

    if queued == 0:
        return jsonify({"status": "error", "error": "ফাইলগুলোতে কোনো ভ্যালিড uid/password entry পাওয়া যায়নি"}), 400

    start_worker_if_needed()
    return jsonify({"status": "success", "queued": queued}), 200


@app.route("/batch/status")
def batch_status():
    with _lock:
        files = [dict(f) for f in BATCH_STATE["files"]]
        running = BATCH_STATE["running"]

    servers = build_summary()
    invalid_list = get_invalid_list()

    totals = {
        "total": sum(f["total"] for f in files),
        "done": sum(f["done"] for f in files),
        "valid": sum(f["valid"] for f in files),
        "invalid": sum(f["invalid"] for f in files),
    }

    return jsonify({
        "files": files,
        "running": running,
        "regions": servers,
        "invalid_list": invalid_list,
        "totals": totals,
    })


@app.route("/region/<region>")
def region_detail(region):
    summary = build_summary()
    r = safe_region(region)
    if r not in summary:
        return jsonify({"error": "Region not found", "levels": []}), 404
    return jsonify(summary[r])


@app.route("/file/<region>/<path:filename>")
def serve_level_file(region, filename):
    r = safe_region(region)
    if ".." in filename or "/" in filename or "\\\\" in filename:
        return jsonify({"error": "bad path"}), 400
    path = os.path.join(VALID_DIR, r, filename)
    if not os.path.isfile(path):
        return jsonify({"error": "not found"}), 404
    return send_file(path, as_attachment=True, download_name=filename)


@app.route("/invalid/download")
def download_invalid():
    if not os.path.isfile(INVALID_FILE):
        with open(INVALID_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    return send_file(INVALID_FILE, as_attachment=True, download_name="invalid.json")


@app.route("/reset", methods=["POST"])
def reset_all():
    with _lock:
        BATCH_STATE["files"] = []
        BATCH_STATE["queue"] = []
        BATCH_STATE["running"] = False
    if os.path.isdir(GUEST_DIR):
        shutil.rmtree(GUEST_DIR)
    os.makedirs(VALID_DIR, exist_ok=True)
    os.makedirs(INVALID_DIR, exist_ok=True)
    with open(INVALID_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, indent=2, ensure_ascii=False)
    return jsonify({"status": "success"}), 200


@app.route("/lookup", methods=["POST"])
def lookup():
    body = request.get_json(silent=True) or {}
    uid = str(body.get("uid", "")).strip()
    password = str(body.get("password", ""))
    if not uid or not password:
        return jsonify({"status": "error", "error": "Both uid and password are required"}), 400
    try:
        login = generate_jwt_token(uid, password)
        real_uid = login.get("real_uid") or uid
        login["_password"] = password
        result = get_account_information(real_uid, login)
        return jsonify({"status": "success", "login": login, "account": result}), 200
    except LoginError as e:
        return jsonify({"status": "error", "stage": e.stage, "error": e.msg}), 500
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/token")
def get_jwt_token():
    uid = request.args.get("uid")
    password = request.args.get("password")
    if not uid or not password:
        return jsonify({"status": "error", "error": "Both uid and password parameters are required"}), 400
    try:
        return jsonify(generate_jwt_token(uid, password)), 200
    except LoginError as e:
        return jsonify({"status": "error", "stage": e.stage, "error": e.msg}), 500
    except Exception as e:
        return jsonify({"status": "error", "error": f"Failed to generate token: {str(e)}"}), 500


# ============================================================
#  ENTRY POINT
# ============================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=False)