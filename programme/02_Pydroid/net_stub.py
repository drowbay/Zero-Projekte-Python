cat > ~/lumi-system/plugins/net_stub.py <<'PY'
import socket

def run(log):
    log("Network-Stub: DNS/Internet-Check ...")
    try:
        socket.gethostbyname("example.com")
        log("DNS OK ✅")
    except Exception as e:
        log(f"DNS FAIL ❌ {e}")
PY
