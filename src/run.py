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
        self.current_preset = 'sidecar'

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

    def get_window_size(self):
        """Get current live window geometry for saving custom gear presets"""
        if webview.windows:
            w = webview.windows[0]
            try:
                cur_w = getattr(w, 'width', self.normal_width) or self.normal_width
                cur_h = getattr(w, 'height', self.normal_height) or self.normal_height
                return {"width": cur_w, "height": cur_h}
            except Exception:
                pass
        return {"width": self.normal_width, "height": self.normal_height}

    def resize_to(self, width: int, height: int):
        """Resize window to arbitrary user-saved custom dimensions"""
        width = max(340, int(width))
        height = max(420, int(height))
        self.normal_width = width
        self.normal_height = height
        self.is_mini = False
        if webview.windows:
            w = webview.windows[0]
            try:
                w.resize(width, height)
                return True
            except Exception:
                pass
        return True

    def set_preset(self, preset_name: str, custom_w: int = None, custom_h: int = None):
        """Switch between 1/4 sidecar ('sidecar'), custom 1 ('custom1'), custom 2 ('custom2'), and mini ('mini')"""
        if preset_name == 'mini':
            self.is_mini = True
            self.current_preset = 'mini'
        elif preset_name in ('custom1', 'custom2'):
            self.is_mini = False
            self.current_preset = preset_name
            if custom_w and custom_h:
                self.normal_width = max(340, int(custom_w))
                self.normal_height = max(420, int(custom_h))
        else:
            self.is_mini = False
            self.current_preset = 'sidecar'

        if webview.windows:
            w = webview.windows[0]
            try:
                sw, sh = 1920, 1080
                if hasattr(webview, 'screens') and webview.screens:
                    primary_screen = webview.screens[0]
                    sw, sh = primary_screen.width, primary_screen.height

                if preset_name == 'mini':
                    w.resize(340, 56)
                elif preset_name in ('custom1', 'custom2') and custom_w and custom_h:
                    target_w = max(340, int(custom_w))
                    target_h = max(420, int(custom_h))
                    self.normal_width = target_w
                    self.normal_height = target_h
                    w.resize(target_w, target_h)
                elif preset_name == 'custom1':  # Fallback default for custom 1 (e.g. 50% half)
                    target_w = max(640, int(sw * 0.45))
                    target_h = max(600, int(sh * 0.9))
                    self.normal_width = target_w
                    self.normal_height = target_h
                    w.resize(target_w, target_h)
                    if hasattr(w, 'move'):
                        w.move(sw - target_w, 10)
                elif preset_name == 'custom2':  # Fallback default for custom 2 (e.g. 70% wide)
                    target_w = max(800, int(sw * 0.65))
                    target_h = max(600, int(sh * 0.92))
                    self.normal_width = target_w
                    self.normal_height = target_h
                    w.resize(target_w, target_h)
                    if hasattr(w, 'move'):
                        w.move(sw - target_w, 10)
                else:  # default 'sidecar' (1/4 screen standard)
                    target_w = max(380, int(sw * 0.28))
                    target_h = max(500, int(sh * 0.88))
                    self.normal_width = target_w
                    self.normal_height = target_h
                    w.resize(target_w, target_h)
                    if hasattr(w, 'move'):
                        w.move(sw - target_w, 10)
            except Exception:
                pass
        return self.current_preset

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
        'easy_drag': False,
        'on_top': True,
        'text_select': True,
        'min_size': (340, 420)
    }
    if x is not None and y is not None:
        window_kwargs['x'] = x
        window_kwargs['y'] = y

    window = webview.create_window(**window_kwargs)
    webview.start()
