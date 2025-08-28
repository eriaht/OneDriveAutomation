import asyncio
import aiohttp
import json
import time
from helpers.sort_versions_numerically import sort_versions_numerically
from helpers.parse_revision_number import parse_revisision_number

# Upper limit for revision number
UPPER_LIMIT = 10

async def check_revision(session, version_key, i):
    revision = f"{version_key[:-4]}{i:04}"
    url = f"https://oneclient.sfx.ms/Win/Installers/{revision}/OneDriveSetup.exe"
    try:
        async with session.get(url, timeout=10) as res:
            if res.status == 200:
                print(f"{revision}: stand alone installer is available ✅")
                return revision
            else:
                print(f"{revision}: stand alone installer is not available ❌")
    except aiohttp.ClientConnectorError:
        print(f"{revision}: Failed to connect to server ❌")
    except aiohttp.ClientOSError:
        print(f"{revision}: Network error occurred ❌")
    except aiohttp.InvalidURL:
        print(f"{revision}: Invalid URL ❌")
    except aiohttp.ServerDisconnectedError:
        print(f"{revision}: Server closed the connection unexpectedly ❌")
    except aiohttp.TooManyRedirects:
        print(f"{revision}: Too many redirects ❌")
    except aiohttp.ClientSSLError:
        print(f"{revision}: SSL error ❌")
    except asyncio.TimeoutError:
        print(f"{revision}: Request timed out after 10 seconds ❌")
    except Exception as e:
        print(f"{revision}: Unknown error ❌ ({e})")
    return None

async def discover_revisions(version_key, version_obj, lower_limit=None):
    if lower_limit is None:
        lower_limit = 1

    try:
        async with aiohttp.ClientSession() as session:
            tasks = [check_revision(session, version_key, i) for i in range(lower_limit, UPPER_LIMIT)]
            
            # Use return_exceptions=True to prevent one failure from stopping all tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Separate successful revisions from exceptions
            successful_revisions = []
            for result in results:
                if isinstance(result, Exception):
                    print(f"{version_key}: Task failed ❌ ({result})")
                elif result is not None:
                    successful_revisions.append(result)

            # Deduplicate and sort
            found = sort_versions_numerically(set(successful_revisions))
            revisions = version_obj[version_key].setdefault("revisions_discovered", [])
            for r in found:
                if r not in revisions:
                    revisions.append(r)

            # Return highest revision found (as int)
            return int(parse_revisision_number(revisions[-1])) if revisions else None

    except Exception as e:
        print(f"{version_key}: Unexpected error during revision discovery ❌ ({e})")
        return None


async def main_async():
    start_time = time.time()

    with open("onedrive_versions.json", "r") as f:
        versions = json.load(f)

    for version in versions:
        version_key = list(version.keys())[0]
        revisions = version[version_key].get("revisions_discovered", [])
        current_revision_number = int(parse_revisision_number(revisions[-1])) if revisions else None

        # Skip if already reached UPPER_LIMIT
        if current_revision_number and current_revision_number >= UPPER_LIMIT:
            print(f"{revisions[-1]} revision number is ≥ upper limit {UPPER_LIMIT}. Skipping. ✈️")
            continue

        # Discover new revisions starting from current revision
        current_revision_number = await discover_revisions(version_key, version, current_revision_number)

    # Save updates
    with open("onedrive_versions.json", "w") as f:
        json.dump(versions, f, indent=4)

    elapsed = (time.time() - start_time) / 60
    print(f"\nScript completed in {elapsed:.2f} minutes")

if __name__ == "__main__":
    asyncio.run(main_async())
