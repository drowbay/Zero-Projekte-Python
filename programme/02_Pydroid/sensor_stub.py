cat > ~/lumi-system/plugins/sensor_stub.py <<'PY'
import random, time

def run(log):
    log("Sensor-Stub startet (simuliert MPU/Magnet/BME) ...")
    for i in range(5):
        data = {
            "accel": [round(random.uniform(-1,1),3) for _ in range(3)],
            "gyro":  [round(random.uniform(-250,250),2) for _ in range(3)],
            "tempC": round(random.uniform(18,32),2),
            "hum%":  round(random.uniform(25,65),2),
        }
        log(f"tick {i}: {data}")
        time.sleep(0.5)
    log("Sensor-Stub fertig ✅")
PY
