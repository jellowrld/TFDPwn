import winreg
import os
import json
import secrets
import string
import subprocess
import sys
import psutil
import time


def get_steam_installation_path():
    """Retrieve the Steam installation path from the Windows registry."""
    try:
        reg_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, 
            r"SOFTWARE\WOW6432Node\Valve\Steam"
        )
        steam_path, _ = winreg.QueryValueEx(reg_key, "InstallPath")
        winreg.CloseKey(reg_key)
        print(f"Steam installation path found: {steam_path}")
        return steam_path
    except FileNotFoundError:
        print("Steam installation path not found in the registry.")
        sys.exit(1)


def generate_random_id(length=32):
    """Generate a random string of letters and digits of a given length."""
    characters = string.ascii_letters + string.digits
    random_id = ''.join(secrets.choice(characters) for _ in range(length))
    print(f"Generated random ID: {random_id}")
    return random_id


def create_settings_file(file_path):
    # Generate random IDs
    print("Generating random IDs...")
    productid = generate_random_id()
    sandboxid = generate_random_id()
    deploymentid = generate_random_id()

    # Define settings data
    settings_data = {
        "title": "The First Descendant",
        "executable": "M1/Binaries/Win64/M1-Win64-Shipping.exe",
        "productid": productid,
        "sandboxid": sandboxid,
        "deploymentid": deploymentid,
        "requested_splash": "EasyAntiCheat/SplashScreen.png",
        "wait_for_game_process_exit": "false",
        "hide_bootstrapper": "false",
        "hide_gui": "false"
    }

    # Write settings data to JSON file
    print(f"Creating directories for file path: {file_path}")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Create directories if not exist
    with open(file_path, 'w') as file:
        json.dump(settings_data, file, indent=4)
    
    print(f"Settings file created at: {file_path}")


def launch_steam_game(app_id):
    # Get the Steam installation path
    steam_path = os.path.join(get_steam_installation_path(), "steam.exe")
    print(f"Checking if Steam exists at: {steam_path}")

    if not os.path.exists(steam_path):
        print("Steam not found. Please check the path.")
        sys.exit(1)

    # Launch the game with the given App ID
    try:
        print(f"Launching TFD with App ID {app_id}...")
        subprocess.run([steam_path, f"steam://rungameid/{app_id}"], check=True)
        print("Game launched successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to launch the game: {e}")
        sys.exit(1)


def find_process_by_name(name):
    """Returns a list of processes matching the name."""
    matching_processes = []
    print(f"Looking for processes with name containing: {name}")
    for process in psutil.process_iter(['pid', 'name']):
        if name.lower() in process.info['name'].lower():
            matching_processes.append(process)
    print(f"Found {len(matching_processes)} matching process(es).")
    return matching_processes


def main():
    # Define file path and App ID
    steam_install_path = get_steam_installation_path()
    file_path = os.path.join(steam_install_path, r"steamapps\common\The First Descendant\EasyAntiCheat\Settings.json")
    app_id = "2074920"  # Example: TFD
    target_process_name = "BlackCipher64.aes"

    # Create the settings file
    print("Creating settings file...")
    create_settings_file(file_path)

    # Launch the Steam game
    print("Launching Steam game...")
    launch_steam_game(app_id)

    print("Watching for processes...")

    # Wait for the target process to start
    while not find_process_by_name(target_process_name):
        print(f"{target_process_name} not found. Checking again...")
        time.sleep(5)

    print(f"{target_process_name} found! Waiting for 1 minute before terminating it...")

    # Wait for 1 minute
    time.sleep(60)

    # Get the target process and terminate it
    print(f"Attempting to terminate {target_process_name}...")
    for process in find_process_by_name(target_process_name):
        try:
            process.terminate()
            process.wait(timeout=5)
            print(f"{target_process_name} terminated successfully.")
        except psutil.NoSuchProcess:
            print(f"{target_process_name} no longer exists.")
        except psutil.AccessDenied:
            print(f"Access denied when trying to terminate {target_process_name}.")
        except psutil.TimeoutExpired:
            print(f"Timeout expired while waiting for {target_process_name} to terminate.")
    
    print("Waiting 10 seconds before exiting...")

    # Wait for 10 seconds before exiting
    time.sleep(10)

    print("Exiting...")


if __name__ == "__main__":
    main()