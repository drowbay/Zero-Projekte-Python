cat > ~/lumi-system/plugins/hello.py <<'PY'
def run(log):
    log("Hello from Lumi Plugin ✨")
    log("Wenn das läuft: Plugin-System funktioniert.")
PY
