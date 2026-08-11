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
        if webview.windows:
            webview.windows[0].destroy()
    def minimize(self):
        if webview.windows:
            webview.windows[0].minimize()
    def toggle_on_top(self):
        if webview.windows:
            w = webview.windows[0]
            try:
                w.on_top = not getattr(w, 'on_top', True)
                return w.on_top
            except Exception:
                return True

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
    
    # Calculate top-right window position (1/4 screen sidecar style)
    width, height = 480, 750
    x, y = None, None
    try:
        if hasattr(webview, 'screens') and webview.screens:
            primary_screen = webview.screens[0]
            sw, sh = primary_screen.width, primary_screen.height
            width = max(380, int(sw * 0.35))
            height = max(500, int(sh * 0.85))
            x = sw - width
            y = 0
    except Exception:
        pass

    window_kwargs = {
        'title': 'Gabriel Control Center',
        'url': f'http://127.0.0.1:{port}/splash',
        'js_api': api,
        'width': width,
        'height': height,
        'frameless': True,
        'resizable': True,
        'easy_drag': True,
        'on_top': True,
        'text_select': True,
        'min_size': (340, 420)
    }
    if x is not None and y is not None:
        window_kwargs['x'] = x
        window_kwargs['y'] = y

    window = webview.create_window(**window_kwargs)
    webview.start()
