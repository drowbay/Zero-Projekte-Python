#!/usr/bin/env bash
# SuSE Buddy v0.1 — Zero Edition
# Quick maintenance + diagnostics for (open)SUSE (incl. proot/Termux setups)

set -Eeuo pipefail

BUDDY_NAME="SuSE Buddy"
LOG_DIR="${HOME}/.suse-buddy"
LOG_FILE="${LOG_DIR}/buddy_$(date +%Y-%m-%d_%H-%M-%S).log"

mkdir -p "$LOG_DIR"

# ---- helpers ----
say()  { echo -e "🟩 $*"; }
warn() { echo -e "🟨 $*" >&2; }
err()  { echo -e "🟥 $*" >&2; }
run()  { echo -e "🔹 $*" | tee -a "$LOG_FILE"; eval "$@" 2>&1 | tee -a "$LOG_FILE"; }

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || { err "Fehlt: $1"; return 1; }
}

detect_env() {
  say "$BUDDY_NAME — Environment Check"
  echo "Timestamp: $(date)" | tee -a "$LOG_FILE"
  echo "User: $(whoami)" | tee -a "$LOG_FILE"
  echo "Kernel: $(uname -a)" | tee -a "$LOG_FILE"
  if [ -f /etc/os-release ]; then
    echo "--- /etc/os-release ---" | tee -a "$LOG_FILE"
    cat /etc/os-release | tee -a "$LOG_FILE"
  fi

  if [ -n "${PROOT_VERSION:-}" ] || grep -qi proot /proc/1/cmdline 2>/dev/null; then
    warn "Sieht nach proot/Termux-Container aus. Manche Systemdienste (systemd, bluetoothd) laufen da nicht."
  fi
}

check_net() {
  say "Network Quick Check"
  if command -v ip >/dev/null 2>&1; then
    run "ip -br a"
    run "ip route || true"
  else
    warn "ip fehlt (iproute2)."
  fi

  # DNS test (ohne ping, weil ping kann in Termux/proot teils geblockt sein)
  if command -v getent >/dev/null 2>&1; then
    run "getent hosts google.com || true"
  else
    warn "getent fehlt (glibc tools)."
  fi

  if command -v curl >/dev/null 2>&1; then
    run "curl -I https://example.com -m 10 || true"
  else
    warn "curl fehlt."
  fi
}

zypper_refresh_update() {
  say "Repos refresh + Update"
  need_cmd zypper || { err "zypper nicht gefunden. Bist du in openSUSE?"; return 1; }
  run "sudo -n true >/dev/null 2>&1 && echo 'sudo: ok' || echo 'sudo: ggf. Passwort nötig'"

  run "sudo zypper --gpg-auto-import-keys refresh"
  run "sudo zypper update -y"
}

install_basics() {
  say "Install Basics (curl, git, nano, unzip, python, pip …)"
  need_cmd zypper || return 1

  # Paketliste: robust & hilfreich
  PKGS=(
    curl git nano vim unzip zip tar gzip
    ca-certificates
    python3 python3-pip
    jq
    iproute2
    openssh
  )

  run "sudo zypper install -y ${PKGS[*]}"
}

python_sanity() {
  say "Python Sanity Check"
  if command -v python3 >/dev/null 2>&1; then
    run "python3 -V"
    run "python3 -m pip -V || true"
    run "python3 - <<'PY'\nimport sys,ssl\nprint('python:',sys.version)\nprint('ssl:',ssl.OPENSSL_VERSION)\nPY"
  else
    warn "python3 fehlt."
  fi
}

disk_mem() {
  say "Disk + Memory"
  run "df -h || true"
  run "free -h || true"
}

fix_ca_certs() {
  say "Fix: CA Certificates (wenn HTTPS zickt)"
  need_cmd zypper || return 1
  run "sudo zypper install -y ca-certificates"
  # update-ca-certificates gibt's je nach SUSE-Packages
  if command -v update-ca-certificates >/dev/null 2>&1; then
    run "sudo update-ca-certificates || true"
  fi
}

show_log() {
  say "Log gespeichert unter:"
  echo "📄 $LOG_FILE"
}

menu() {
  echo
  echo "=============================="
  echo "   ${BUDDY_NAME}  (v0.1)"
  echo "=============================="
  echo "1) Environment Check"
  echo "2) Network Check"
  echo "3) zypper refresh + update"
  echo "4) Install Basics"
  echo "5) Python Sanity"
  echo "6) Disk + Memory"
  echo "7) Fix CA Certificates"
  echo "8) Run ALL (empfohlen)"
  echo "0) Exit"
  echo
  read -r -p "Choose: " choice
  echo

  case "$choice" in
    1) detect_env ;;
    2) check_net ;;
    3) zypper_refresh_update ;;
    4) install_basics ;;
    5) python_sanity ;;
    6) disk_mem ;;
    7) fix_ca_certs ;;
    8) detect_env; check_net; zypper_refresh_update || true; install_basics || true; python_sanity; disk_mem; fix_ca_certs || true ;;
    0) exit 0 ;;
    *) warn "Ungültig." ;;
  esac

  show_log
}

# ---- entry ----
menu
