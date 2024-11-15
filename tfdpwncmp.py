import json
import os
import secrets
import string
import subprocess
import sys
import psutil
import time

def generate_random_id(length=32):
    """Generate a random string of letters and digits of a given length."""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

def create_settings_file(file_path):
    """Create the settings JSON file with random IDs."""
    settings_data = {
        "title": "The First Descendant",
        "executable": "M1/Binaries/Win64/M1-Win64-Shipping.exe",
        "productid": generate_random_id(),
        "sandboxid": generate_random_id(),
        "deploymentid": generate_random_id(),
        "requested_splash": "EasyAntiCheat/SplashScreen.png",
        "wait_for_game_process_exit": "false",
        "hide_bootstrapper": "false",
        "hide_gui": "false"
    }
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as file:
        json.dump(settings_data, file, indent=4)
    print(f"Settings file created at: {file_path}")

def launch_steam_game(app_id):
    """Launch the game via Steam using the App ID."""
    steam_path = r"C:\Program Files (x86)\Steam\steam.exe"
    if not os.path.exists(steam_path):
        print("Steam not found. Check the path.")
        sys.exit(1)
    subprocess.run([steam_path, f"steam://rungameid/{app_id}"], check=True)

def find_process_by_name(name):
    """Return a list of processes matching the name."""
    return [p for p in psutil.process_iter(['pid', 'name']) if name.lower() in p.info['name'].lower()]

def main():
    file_path = r"C:\Program Files (x86)\Steam\steamapps\common\The First Descendant\EasyAntiCheat\Settings.json"
    app_id = "2074920"
    target_process_name = "BlackCipher64.aes"

    create_settings_file(file_path)
    launch_steam_game(app_id)

    print("Watching for target process...")
    while not find_process_by_name(target_process_name):
        time.sleep(5)

    print(f"{target_process_name} found! Waiting 1 minute before termination.")
    time.sleep(60)

    for process in find_process_by_name(target_process_name):
        try:
            process.terminate()
            process.wait(timeout=5)
            print(f"Terminated: {process.info['name']} (PID {process.pid})")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired) as e:
            print(f"Error terminating process: {e}")

    print("Exiting in 10 seconds...")
    time.sleep(10)

if __name__ == "__main__":
    main()