import requests
import json
from bs4 import BeautifulSoup
from helpers.check_date import check_date
from helpers.parse_date import parse_date

def main():
    
    hansbrender_html = requests.get("https://hansbrender.com/all-onedrive-versions-windows/")

    soup = BeautifulSoup(hansbrender_html.text, "lxml")

    # Find all table rows
    rows = soup.find_all("tr")

    # Final result list
    result = []

    for index, row in enumerate(rows):
        # Skip first row with column names
        if (index == 0):
            continue

        # Test
        # if (index > 3):
        #     break

        cols = row.find_all("td")
        
        # Skip row if it does not contain all column data
        if len(cols) < 3:
            continue

        date = parse_date(cols[0].text.strip())

        # Check if version is older than 2 years, if it is break loop. We only support versions as far as 2 years back
        if (not check_date(date, 2)):
            break

        version = cols[1].text.strip()

        # Extract ring type
        ring = None
        if "production" in cols[2].text.lower():
            ring = "current production" if len(cols[2].find_all("strong")) else "production"
        elif "insider" in cols[2].text.lower():
            ring = "current insider" if len(cols[2].find_all("strong")) else "insider"

        # Extract architecture labels (32Bit, 64Bit, ARM64)
        arch_links = cols[2].find_all("a")
        architectures = [a.text.strip().lower() for a in arch_links]

        # Normalize architecture casing
        architectures = [arch.lower() for arch in architectures]

        # Create dictionary per version
        version_info = {
            version: {
                "date": date,
                "ring": ring,
                "architectures": architectures,
                "revisions_discovered": [],
                "versions_installed": []
            }
        }

        result.append(version_info)


    json_data = json.dumps(result, indent=4)

    with open("onedrive_versions.json", "w") as onedrive_versions:
        onedrive_versions.write(json_data)

if __name__ == "__main__":
    main()