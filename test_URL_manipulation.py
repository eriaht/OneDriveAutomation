import requests

version = "25.127.0701.0006"

for i in range(1, 10):
    print(f"Checking OneDrive version: {version[0: -1]}{i}", end=" ")

    res = requests.get(f"https://oneclient.sfx.ms/Win/Installers/{version[0: -1]}{i}/OneDriveSetup.exe", stream=True)

    status = res.status_code

    if status == 200:
        print("Stand alone installer is available ✅")
    else:
        print("Stand alone installer is not available ❌")

