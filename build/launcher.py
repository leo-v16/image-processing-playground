import subprocess
import sys
import importlib.util
import os

# 1. LIST YOUR DEPENDENCIES HERE
REQUIRED_PACKAGES = [
    ("dearpygui", "dearpygui"), # (Import Name, Pip Install Name)
    ("PIL", "Pillow"),
    ("numpy", "numpy")
]

def check_pip():
    """Checks if pip is available in the system."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def install_package(package_name):
    """Attempts to install a package via pip."""
    print(f"[BOOTSTRAP] Installing {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except Exception as e:
        print(f"[ERROR] Failed to install {package_name}: {e}")
        return False

def bootstrap():
    print("--- Environment Check ---")
    
    # Check for Pip first
    if not check_pip():
        print("!! CRITICAL ERROR !!")
        print("Python is installed, but 'pip' was not found.")
        print("Please reinstall Python and ensure 'Add to PATH' and 'pip' are checked.")
        input("Press Enter to exit...")
        sys.exit(1)

    # Check and install packages
    for import_name, pip_name in REQUIRED_PACKAGES:
        if importlib.util.find_spec(import_name) is None:
            print(f"[!] {pip_name} is missing.")
            if not install_package(pip_name):
                print(f"!! ERROR: Could not resolve dependency: {pip_name}")
                input("Press Enter to exit...")
                sys.exit(1)
        else:
            print(f"[OK] {pip_name} is ready.")

    # Check for your C++ DLL
    if not os.path.exists("./process.dll"):
        print("!! WARNING: process.dll not found in the current directory.")
        print("The UI will open, but image processing will not work.")
        input("Press Enter to continue anyway...")

    print("--- Environment Ready ---\n")

    # 2. LAUNCH YOUR MAIN SCRIPT
    try:
        import main # This assumes your file is named main.py
        app = main.ImageNodeApp()
        app.run()
    except Exception as e:
        print(f"[CRASH] The application encountered an error: {e}")
        input("Press Enter to close...")

if __name__ == "__main__":
    bootstrap()