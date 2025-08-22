import requests
import json
from bs4 import BeautifulSoup


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

    cols = row.find_all("td")
    if len(cols) < 3:
        continue

    date = cols[0].text.strip()
    version = cols[1].text.strip()

    # Extract architecture labels (32Bit, 64Bit, ARM64)
    arch_links = cols[2].find_all("a")
    # fix and only add architectures with anchor tags
    architectures = [a.text.strip().lower() for a in arch_links]
    # print(architectures)

    # Normalize architecture casing
    architectures = [arch.lower() for arch in architectures]

    # Create dictionary per version
    version_info = {
        version: {
            "date": date,
            "ring": "insiders",
            "architectures": architectures,
            "subversions": []
        }
    }

    result.append(version_info)

json_data = json.dumps(result, indent=4)

with open("onedrive_versions.json", "w") as onedrive_versions:
    onedrive_versions.write(json_data)






