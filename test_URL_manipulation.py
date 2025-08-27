import asyncio
import aiohttp
import json
import time
from helpers.sort_versions_numerically import sort_versions_numerically

async def check_revision(session, version_key, i):
    revision = f"{version_key[:-4]}{i:04}"
    url = f"https://oneclient.sfx.ms/Win/Installers/{revision}/OneDriveSetup.exe"
    try:
        async with session.get(url, timeout=5) as res:
            if res.status == 200:
                print(f"{revision}: stand alone installer is available ✅")
                return revision
            else:
                print(f"{revision}: stand alone installer is not available ❌")
    except Exception:
        print(f"{revision}: Request failed ❌")
    return None

async def discover_revisions(version_key, version_obj):
    async with aiohttp.ClientSession() as session:
        tasks = [check_revision(session, version_key, i) for i in range(1, 10)] # Adjust to start loop from highest revision number discovered
        # Runs all tasks concurrently and waits for all of them to finish
        results = await asyncio.gather(*tasks)
        # Filter out None and deduplicate
        found = sort_versions_numerically({r for r in results if r})
        if "revisions_discovered" in version_obj[version_key] and isinstance(version_obj[version_key]["revisions_discovered"], list):
            version_obj[version_key]["revisions_discovered"].extend(
                [r for r in found if r not in version_obj[version_key]["revisions_discovered"]]
            )

async def main_async():
    start_time = time.time()

    with open("onedrive_versions.json", "r") as f:
        versions = json.load(f)

    for version in versions:
        version_key = list(version.keys())[0]
        await discover_revisions(version_key, version)

    with open("onedrive_versions.json", "w") as f:
        json.dump(versions, f, indent=4)

    elapsed = (time.time() - start_time) / 60
    print(f"\nScript completed in {elapsed:.2f} minutes")

if __name__ == "__main__":
    asyncio.run(main_async())
