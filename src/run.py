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
    def __init__(self):
        self.normal_width = 480
        self.normal_height = 750
        self.is_mini = False

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

    def toggle_mini_mode(self, is_mini: bool = None):
        if webview.windows:
            w = webview.windows[0]
            try:
                if is_mini is None:
                    self.is_mini = not self.is_mini
                else:
                    self.is_mini = bool(is_mini)
                
                if self.is_mini:
                    self.normal_width = getattr(w, 'width', self.normal_width) or self.normal_width
                    self.normal_height = getattr(w, 'height', self.normal_height) or self.normal_height
                    w.resize(340, 56)
                else:
                    w.resize(self.normal_width, self.normal_height)
                return self.is_mini
            except Exception:
                return False
        return False

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
