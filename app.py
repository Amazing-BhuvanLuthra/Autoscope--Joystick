from flask import Flask, render_template
import subprocess

app = Flask(__name__)

def is_bluetooth_available():
    try:
        output = subprocess.check_output(["bluetoothctl", "show"])
        return b"Powered: yes" in output
    except Exception as e:
        print("Error:", e)
        return False

def discover_devices():
    if is_bluetooth_available():
        try:
            nearby_devices = subprocess.check_output(["hcitool", "scan"]).decode("utf-8")
            return [line.split("\t") for line in nearby_devices.split("\n") if len(line) > 0]
        except Exception as e:
            print("Error:", e)
    return []

@app.route('/')
def index():
    nearby_devices = discover_devices()
    return render_template('index.html', nearby_devices=nearby_devices)

@app.route('/connect/<address>')
def connect(address):
    return f"Connecting to {address}..."

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
