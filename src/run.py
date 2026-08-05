import threading
import uvicorn
import webview
import time
import os
import sys

import socket

# Change directory to ensure static files are found when running from compiled exe
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)
else:
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from main import app

class WindowApi:
    def close(self):
        webview.windows[0].destroy()
    def minimize(self):
        webview.windows[0].minimize()

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

def start_server(port):
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="critical")

if __name__ == '__main__':
    port = get_free_port()
    # Start the FastAPI server in a background thread
    t = threading.Thread(target=start_server, args=(port,), daemon=True)
    t.start()
    # Wait slightly for uvicorn to bind the port
    time.sleep(0.5)
    
    api = WindowApi()
    
    # Create the webview window pointing to the splash screen via FastAPI
    window = webview.create_window(
        'Gabriel Control Center', 
        f'http://127.0.0.1:{port}/splash',
        js_api=api,
        width=1000,
        height=700,
        frameless=False,
        transparent=False,
        text_select=True,
        on_top=True
    )
    
    # Start the webview application block
    webview.start()
