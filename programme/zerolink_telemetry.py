import tkinter as tk
from tkinter import ttk
import psutil
import socket
import time
import threading
import subprocess
import platform


class ZeroLinkTelemetryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ZeroLink Telemetry - Device & AI Health")
        self.root.geometry("720x520")
        self.root.minsize(640, 480)

        self.last_net = psutil.net_io_counters()
        self.last_time = time.time()

        self.build_ui()
        self.update_loop()

    def build_ui(self):
        title = tk.Label(
            self.root,
            text="ZeroLink Telemetry",
            font=("Segoe UI", 22, "bold")
        )
        title.pack(pady=10)

        subtitle = tk.Label(
            self.root,
            text="Keine privaten Daten. Nur technischer Zustand.",
            font=("Segoe UI", 11)
        )
        subtitle.pack(pady=2)

        self.main_frame = ttk.Frame(self.root, padding=15)
        self.main_frame.pack(fill="both", expand=True)

        self.device_box = ttk.LabelFrame(self.main_frame, text="Geräte-Zustand", padding=12)
        self.device_box.pack(fill="x", pady=8)

        self.network_box = ttk.LabelFrame(self.main_frame, text="Netzwerk-Telemetrie", padding=12)
        self.network_box.pack(fill="x", pady=8)

        self.ai_box = ttk.LabelFrame(self.main_frame, text="KI-Zustand", padding=12)
        self.ai_box.pack(fill="x", pady=8)

        self.status_box = ttk.LabelFrame(self.main_frame, text="Bewertung", padding=12)
        self.status_box.pack(fill="x", pady=8)

        self.labels = {}

        self.add_row(self.device_box, "system", "System:")
        self.add_row(self.device_box, "cpu", "CPU:")
        self.add_row(self.device_box, "ram", "RAM:")
        self.add_row(self.device_box, "battery", "Akku/Strom:")
        self.add_row(self.device_box, "uptime", "Laufzeit:")

        self.add_row(self.network_box, "internet", "Internet:")
        self.add_row(self.network_box, "ping", "Ping:")
        self.add_row(self.network_box, "upload", "Upload:")
        self.add_row(self.network_box, "download", "Download:")
        self.add_row(self.network_box, "hostname", "Hostname:")

        self.add_row(self.ai_box, "ai_local", "Lokale KI:")
        self.add_row(self.ai_box, "ai_state", "KI-Arbeitszustand:")
        self.add_row(self.ai_box, "ai_note", "Hinweis:")

        self.add_row(self.status_box, "influence", "Einfluss auf System:")
        self.add_row(self.status_box, "recommendation", "Empfehlung:")

    def add_row(self, parent, key, text):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=3)

        left = ttk.Label(frame, text=text, width=22)
        left.pack(side="left")

        right = ttk.Label(frame, text="...", anchor="w")
        right.pack(side="left", fill="x", expand=True)

        self.labels[key] = right

    def set_label(self, key, value):
        self.labels[key].config(text=value)

    def check_internet(self):
        try:
            socket.create_connection(("1.1.1.1", 53), timeout=2)
            return True
        except OSError:
            return False

    def ping_host(self, host="1.1.1.1"):
        try:
            param = "-n" if platform.system().lower() == "windows" else "-c"
            command = ["ping", param, "1", host]
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=3
            )

            output = result.stdout.lower()

            if "zeit=" in output:
                part = output.split("zeit=")[1].split("ms")[0]
                return f"{part.strip()} ms"
            if "time=" in output:
                part = output.split("time=")[1].split("ms")[0]
                return f"{part.strip()} ms"

            if result.returncode == 0:
                return "erreichbar"
            return "nicht erreichbar"
        except Exception:
            return "nicht messbar"

    def format_bytes_speed(self, value):
        if value < 1024:
            return f"{value:.0f} B/s"
        elif value < 1024 * 1024:
            return f"{value / 1024:.1f} KB/s"
        else:
            return f"{value / (1024 * 1024):.2f} MB/s"

    def get_network_speed(self):
        current_net = psutil.net_io_counters()
        current_time = time.time()

        elapsed = max(current_time - self.last_time, 0.1)

        upload_speed = (current_net.bytes_sent - self.last_net.bytes_sent) / elapsed
        download_speed = (current_net.bytes_recv - self.last_net.bytes_recv) / elapsed

        self.last_net = current_net
        self.last_time = current_time

        return upload_speed, download_speed

    def get_battery_status(self):
        battery = psutil.sensors_battery()

        if battery is None:
            return "kein Akku erkannt / Desktop-PC"

        percent = battery.percent
        plugged = battery.power_plugged

        if plugged:
            return f"{percent}% - wird geladen / Netzstrom"
        return f"{percent}% - Akku läuft"

    def get_uptime(self):
        boot_time = psutil.boot_time()
        uptime_seconds = int(time.time() - boot_time)

        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60

        return f"{hours}h {minutes}min"

    def detect_local_ai(self):
        """
        Einfache Erkennung.
        Später können wir hier Ollama, LM Studio, KoboldCPP oder lokale APIs richtig abfragen.
        """
        possible_processes = [
            "ollama",
            "lmstudio",
            "koboldcpp",
            "python",
            "text-generation-webui"
        ]

        found = []

        for proc in psutil.process_iter(["name"]):
            try:
                name = (proc.info["name"] or "").lower()
                for target in possible_processes:
                    if target in name:
                        found.append(proc.info["name"])
            except Exception:
                pass

        if found:
            unique = sorted(set(found))
            return "aktiv möglich: " + ", ".join(unique[:5])

        return "keine lokale KI erkannt"

    def calculate_influence(self, cpu, ram, upload, download, internet_ok):
        score = 0
        reasons = []

        if cpu > 85:
            score += 2
            reasons.append("CPU hoch")

        if ram > 85:
            score += 2
            reasons.append("RAM fast voll")

        if upload > 2 * 1024 * 1024:
            score += 1
            reasons.append("Upload erhöht")

        if download > 8 * 1024 * 1024:
            score += 1
            reasons.append("Download erhöht")

        if not internet_ok:
            score += 3
            reasons.append("Internet gestört")

        if score <= 1:
            level = "niedrig"
        elif score <= 3:
            level = "mittel"
        else:
            level = "hoch"

        if not reasons:
            reasons_text = "alles stabil"
        else:
            reasons_text = ", ".join(reasons)

        return f"{level} ({reasons_text})"

    def recommendation_text(self, cpu, ram, internet_ok):
        if not internet_ok:
            return "Router/Internet prüfen. DNS oder Verbindung könnte hängen."

        if cpu > 85:
            return "CPU ist stark belastet. Hintergrundprogramme prüfen."

        if ram > 85:
            return "RAM ist knapp. Browser/Tabs/Launcher checken."

        return "System sieht stabil aus. Guter Zustand, Maschine schnurrt."

    def update_loop(self):
        def worker():
            cpu = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory().percent
            upload, download = self.get_network_speed()
            internet_ok = self.check_internet()
            ping = self.ping_host()

            hostname = socket.gethostname()
            system_name = f"{platform.system()} {platform.release()}"

            battery = self.get_battery_status()
            uptime = self.get_uptime()
            ai_status = self.detect_local_ai()

            influence = self.calculate_influence(cpu, ram, upload, download, internet_ok)
            recommendation = self.recommendation_text(cpu, ram, internet_ok)

            internet_text = "online" if internet_ok else "offline / gestört"

            if "keine lokale KI" in ai_status:
                ai_state = "ruhig / keine Last erkannt"
                ai_note = "Später können wir Ollama oder LM Studio direkt auslesen."
            else:
                ai_state = "möglicherweise aktiv"
                ai_note = "KI-Prozess erkannt. Genauere Telemetrie bauen wir als nächstes."

            self.root.after(0, lambda: self.set_label("system", system_name))
            self.root.after(0, lambda: self.set_label("cpu", f"{cpu}%"))
            self.root.after(0, lambda: self.set_label("ram", f"{ram}%"))
            self.root.after(0, lambda: self.set_label("battery", battery))
            self.root.after(0, lambda: self.set_label("uptime", uptime))

            self.root.after(0, lambda: self.set_label("internet", internet_text))
            self.root.after(0, lambda: self.set_label("ping", ping))
            self.root.after(0, lambda: self.set_label("upload", self.format_bytes_speed(upload)))
            self.root.after(0, lambda: self.set_label("download", self.format_bytes_speed(download)))
            self.root.after(0, lambda: self.set_label("hostname", hostname))

            self.root.after(0, lambda: self.set_label("ai_local", ai_status))
            self.root.after(0, lambda: self.set_label("ai_state", ai_state))
            self.root.after(0, lambda: self.set_label("ai_note", ai_note))

            self.root.after(0, lambda: self.set_label("influence", influence))
            self.root.after(0, lambda: self.set_label("recommendation", recommendation))

            self.root.after(2000, self.update_loop)

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = ZeroLinkTelemetryApp(root)
    root.mainloop()