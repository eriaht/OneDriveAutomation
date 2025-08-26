import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

def discover_revisions(version_key, version_obj):
    for i in range(1, 10):
        revision = f"{version_key[0: -4]}{i:04}"

        print(f"Checking OneDrive version: {revision}", end=" ")

        res = requests.get(f"https://oneclient.sfx.ms/Win/Installers/{revision}/OneDriveSetup.exe", stream=True)

        status = res.status_code

        if status == 200:
            print("Stand alone installer is available ✅")
            version_obj[version_key]["revisions_discovered"].append(revision)
        else:
            print("Stand alone installer is not available ❌")

# --- concurrent check_revision function ---
def check_revision(version_key, i, session):
    revision = f"{version_key[:-4]}{i:04}"

    try:
        res = session.get(f"https://oneclient.sfx.ms/Win/Installers/{revision}/OneDriveSetup.exe", stream=True, timeout=5)
        if res.status_code == 200:
            print(f"{revision}: stand alone installer is available ✅")
            return revision
        else:
            print(f"{revision}: stand alone installer is not available ❌")
    except requests.RequestException:
        print("Request failed ❌")
    return None

# --- concurrent discover_revisions ---
def discover_revisions(version_key, version_obj):
    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(check_revision, version_key, i, session) for i in range(1, 10)]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    version_obj[version_key]["revisions_discovered"].append(result)
                    version_obj[version_key]["revisions_discovered"] = list(set(version_obj[version_key]["revisions_discovered"]))

def main():
    start_time = time.time()  # start timer

    with open("onedrive_versions.json", "r+") as onedrive_versions:
        versions = json.load(onedrive_versions)

    for version in versions:
        discover_revisions(list(version.keys())[0], version)

    with open("onedrive_versions.json", "w") as f:
        json.dump(versions, f, indent=4)

    end_time = time.time()  # end timer
    elapsed_minutes = (end_time - start_time) / 60
    print(f"\nScript completed in {elapsed_minutes:.2f} minutes")    
    
if __name__ == "__main__":
    main()