from flask import Flask
import threading

app = Flask(__name__)

@app.route('/health')
def health_check():
    return "OK", 200

def start_health_server():
    """Run health check server in background"""
    def run():
        app.run(host='0.0.0.0', port=3000)
        
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
