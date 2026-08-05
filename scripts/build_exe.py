import os
import subprocess
import sys

def build():
    print("🚀 [Gabriel Build System] Starting standalone executable compilation...")
    
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
    print("⚙️  Running PyInstaller...")
    # Build command for Windows
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",
        "--windowed", # Don't open console window when running the app
        "--add-data", f"static{os.pathsep}static",
        "--add-data", f"src{os.pathsep}src",
        "--name", "Gabriel_Agent_OS",
        "src/main.py"
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ Build Successful!")
        print(f"📦 Your standalone executable is located in: {os.path.abspath('dist/Gabriel_Agent_OS')}")
        print("💡 You can now zip this folder and distribute it as a zero-setup application.")
    else:
        print("\n❌ Build Failed. Check the logs above.")

if __name__ == "__main__":
    build()
