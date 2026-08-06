# Autostart Configuration

This guide provides instructions on how to configure Gabriel to start automatically on system boot in the background without popping up a terminal window.

## Windows (Task Scheduler)
To run Gabriel silently on Windows startup:
1. Open **Task Scheduler** (search in the Start Menu).
2. Click **Action** -> **Create Basic Task...**
3. Name it "Gabriel Background Service" and click **Next**.
4. Choose **When the computer starts** or **When I log on**, then click **Next**.
5. Select **Start a program** and click **Next**.
6. In **Program/script**, browse and select the `Launch_Gabriel.vbs` script located in the `scripts` folder of this project.
7. Click **Finish**.

This will use the `.vbs` script to run the Python server invisibly in the background.

## macOS (launchd)
Create a `.plist` file (e.g., `com.gabriel.server.plist`) in `~/Library/LaunchAgents/` with the following content:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.gabriel.server</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>cd /path/to/Gabriel && source venv/bin/activate && python src/main.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/gabriel.out</string>
    <key>StandardErrorPath</key>
    <string>/tmp/gabriel.err</string>
</dict>
</plist>
```
*Remember to replace `/path/to/Gabriel` with the actual path to your repository.*

Then load it:
```bash
launchctl load ~/Library/LaunchAgents/com.gabriel.server.plist
```

## Linux (systemd)
Create a service file at `~/.config/systemd/user/gabriel.service` (or `/etc/systemd/system/gabriel.service` for system-wide):

```ini
[Unit]
Description=Gabriel Control Center
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/Gabriel
ExecStart=/path/to/Gabriel/venv/bin/python src/main.py
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
```
*Remember to replace `/path/to/Gabriel` with the actual path to your repository.*

Enable and start the service:
```bash
systemctl --user enable gabriel
systemctl --user start gabriel
```
