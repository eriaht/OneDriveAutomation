import requests
from bs4 import BeautifulSoup
import json

def fetch_onedrive_versions(url):
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    records = []

    # Locate the table or preformatted list containing the version entries
    # Based on the page HTML, entries appear as lines with date, version, ring, and download links
    content_div = soup.find('div', class_='entry-content')  # adjust if needed

    # The lines are likely in text nodes or paragraphs
    lines = []
    for elem in content_div.find_all(['p', 'li']):
        text = elem.get_text(strip=True)
        if text and text[0].isdigit():
            lines.append(elem)

    for elem in lines:
        text = elem.get_text(separator=' ', strip=True)
        parts = text.split()
        # Expected structure:
        # [DATE] [VERSION] (maybe ▶️Production Ring) [Insider/Production] Version Download
        # But links are inside <a> tags. Let's extract anchor tags separately.

        # Extract date, version, ring/type
        tokens = text.split()
        date = tokens[0]
        version = tokens[1]
        ring_type = 'Insider'
        if 'Production' in text:
            ring_type = 'Production Ring'

        # Find links for architectures
        links = {'32Bit': None, '64Bit': None, 'ARM64': None}
        for link in elem.find_all('a'):
            link_text = link.get_text(strip=True)
            href = link['href']
            if '32Bit' in link_text:
                links['32Bit'] = href
            elif '64Bit' in link_text:
                links['64Bit'] = href
            elif 'ARM64' in link_text:
                links['ARM64'] = href

        record = {
            'date': date,
            'version': version,
            'ring_type': ring_type,
            'downloads': links
        }
        records.append(record)

    return records

def save_to_json(records, out_file='onedrive_versions.json'):
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

def main():
    url = 'https://hansbrender.com/all-onedrive-versions-windows/'
    versions = fetch_onedrive_versions(url)
    save_to_json(versions)
    print(f"Saved {len(versions)} versions to JSON.")

if __name__ == '__main__':
    main()
