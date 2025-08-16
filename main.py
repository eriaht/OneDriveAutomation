import requests
import subprocess
import os
import time
import psutil  # pip install psutil

# Official Microsoft download link for OneDrive installer (Windows x64)
ONEDRIVE_URL = "https://oneclient.sfx.ms/Win/Installers/25.149.0803.0002/amd64/OneDriveSetup.exe"
INSTALLER_PATH = "OneDriveSetup.exe"
ONEDRIVE_EXE = r"C:\Program Files\Microsoft OneDrive\OneDrive.exe"

# remove amd64 and use Program Files (x86) for 32 bit install

# ONEDRIVE_EXE = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\OneDrive\OneDrive.exe") per user install

def download_installer():
    print("[+] Downloading OneDrive installer...")
    response = requests.get(ONEDRIVE_URL, stream=True)
    response.raise_for_status()

    with open(INSTALLER_PATH, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    print("[+] Download complete.")

def run_installer():
    print("[+] Running OneDrive installer as system-wide...")
    proc = subprocess.Popen(
        ["OneDriveSetup.exe", "/allusers", "/silent"],
        shell=True
    )
    proc.wait()
    print("[+] Installer process exited.")

# def wait_for_install(timeout=300):
#     print("[+] Waiting for OneDrive installation to complete...")
#     start_time = time.time()

#     while time.time() - start_time < timeout:
#         if os.path.exists(ONEDRIVE_EXE):
#             print("[+] OneDrive.exe found.")
#             return True
#         time.sleep(5)

#     print("[-] Timed out waiting for installation.")
#     return False

def ensure_installer_finished():
    print("[+] Ensuring OneDriveSetup.exe has fully finished...")
    while any("OneDriveSetup.exe" in p.name() for p in psutil.process_iter(['name'])):
        time.sleep(2)
    print("[+] Installer is no longer running.")


def check_for_update():
    print("[+] Checking for OneDrive updates...")
    if os.path.exists(ONEDRIVE_EXE):
        # subprocess.run([ONEDRIVE_EXE, "/update"], check=True)
        subprocess.run(INSTALLER_PATH, check=True)
        print("[+] Update check complete.")
    else:
        print("[-] OneDrive.exe not found. Cannot check for updates.")

def uninstall():
    try:
        subprocess.run([INSTALLER_PATH,"/uninstall"], check=True)
        print("Uninstallation completed.")
    except subprocess.CalledProcessError as e:
        if e.returncode == 2147747483:
            print("OneDrive is not installed or cannot be uninstalled for this user.")
        else:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    download_installer()
    run_installer()
    ensure_installer_finished()

    check_for_update()
    time.sleep(10)
    uninstall()
