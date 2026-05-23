import os
import re
import sys
import csv
import json
import urllib.request
import urllib.error

CSV_URL = "https://temaetfs.com/hubfs/Website/Holdings/NASA-holdings.csv"
WEB_URL = "https://temaetfs.com/nasa"

def fetch_content(url):
    """Fetches text content from a URL using urllib."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            return response.read()
    except urllib.error.URLError as e:
        print(f"Error fetching URL {url}: {e}", file=sys.stderr)
        raise

def parse_holdings_csv(csv_bytes):
    """Parses holdings CSV to extract holdings date, Top 10, and SpaceX SPV shares."""
    csv_text = csv_bytes.decode('utf-8', errors='ignore').splitlines()
    reader = csv.DictReader(csv_text)
    
    holdings = []
    spacex_row = None
    
    for row in reader:
        # Validate row has the required fields
        if not row.get('holdings_date') or not row.get('proper_name'):
            continue
            
        holdings.append(row)
        
        # Check for SpaceX SPV
        ticker = row.get('ticker', '').strip().upper()
        name = row.get('proper_name', '').strip().upper()
        if ticker == 'SPACEX SPV' or 'SPACEX' in name:
            spacex_row = row

    if not holdings:
        raise ValueError("No valid holdings parsed from CSV.")
    
    # Get the holdings date from the first row
    holdings_date = holdings[0]['holdings_date'].strip()
    
    # Sort holdings by percent_of_nav descending to ensure top 10 order
    # (some CSV files might not be perfectly sorted)
    def get_weight(row):
        try:
            return float(row.get('percent_of_nav', 0))
        except ValueError:
            return 0.0
            
    holdings.sort(key=get_weight, reverse=True)
    
    # Format top 10
    top10 = []
    for idx, row in enumerate(holdings[:10]):
        try:
            weight_pct = float(row.get('percent_of_nav', 0)) * 100
        except ValueError:
            weight_pct = 0.0
            
        try:
            shares = float(row.get('shares', 0)) if row.get('shares') else 0.0
        except ValueError:
            shares = 0.0
            
        top10.append({
            "rank": idx + 1,
            "ticker": row.get('ticker', '').strip(),
            "name": row.get('proper_name', '').strip(),
            "weight": round(weight_pct, 4),
            "shares": shares
        })
        
    # SpaceX SPV specific shares from CSV
    spacex_spv_shares = 0.0
    if spacex_row:
        try:
            spacex_spv_shares = float(spacex_row.get('shares', 0)) if spacex_row.get('shares') else 0.0
        except ValueError:
            pass
            
    return holdings_date, top10, spacex_spv_shares

def scrape_spacex_common_shares(html_bytes):
    """Scrapes the SpaceX common share equivalents from the NASA ETF webpage HTML."""
    html_text = html_bytes.decode('utf-8', errors='ignore')
    
    # Multiple robust patterns to match SpaceX share equivalents in text
    patterns = [
        r"NASA holds\s+([\d,]+)(?:&nbsp;|\s)+common share equivalents",
        r"holds\s+([\d,]+)(?:&nbsp;|\s)+common share equivalents",
        r"([\d,]+)(?:&nbsp;|\s)+common share equivalents",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html_text, re.IGNORECASE)
        if match:
            shares_str = match.group(1)
            try:
                shares = int(shares_str.replace(",", ""))
                return shares
            except ValueError:
                continue
                
    print("Warning: Could not parse SpaceX common share equivalents from webpage. Defaulting to 0.", file=sys.stderr)
    return 0

def sync_to_google_sheet(webapp_url, payload):
    """Posts the payload to the Google Apps Script Web App URL."""
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        webapp_url,
        data=data,
        headers={'Content-Type': 'application/json', 'User-Agent': 'Python-Urllib'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            resp_bytes = response.read()
            resp_str = resp_bytes.decode('utf-8')
            print("Google Sheet Sync Response:", resp_str)
            return json.loads(resp_str)
    except urllib.error.URLError as e:
        print(f"Error syncing with Google Sheet: {e}", file=sys.stderr)
        raise

def main():
    # Read the Web App URL from the environment variable (supplied via GitHub Secrets)
    webapp_url = os.environ.get("GOOGLE_SHEET_WEBAPP_URL")
    if not webapp_url:
        print("CRITICAL ERROR: Environment variable GOOGLE_SHEET_WEBAPP_URL is not set.", file=sys.stderr)
        print("Please configure this in your GitHub Action secrets.", file=sys.stderr)
        sys.exit(1)
        
    print("Step 1: Downloading holdings CSV...")
    csv_bytes = fetch_content(CSV_URL)
    
    print("Step 2: Parsing holdings CSV...")
    holdings_date, top10, spacex_spv_shares = parse_holdings_csv(csv_bytes)
    print(f"Parsed Date: {holdings_date}")
    print(f"SpaceX SPV Shares (from CSV): {spacex_spv_shares}")
    print("Top 10 Holdings found:")
    for h in top10:
        print(f"  {h['rank']}. {h['name']} ({h['ticker']}) - {h['weight']}% - {h['shares']} shares")
        
    print("Step 3: Fetching and scraping NASA ETF webpage for SpaceX common shares...")
    html_bytes = fetch_content(WEB_URL)
    spacex_common_shares = scrape_spacex_common_shares(html_bytes)
    print(f"SpaceX Common Share Equivalents: {spacex_common_shares}")
    
    # Package data
    payload = {
        "date": holdings_date,
        "top10": top10,
        "spacex_spv_shares": spacex_spv_shares,
        "spacex_common_shares": spacex_common_shares
    }
    
    print("Step 4: Syncing data to Google Sheet...")
    sync_to_google_sheet(webapp_url, payload)
    print("Sync complete successfully!")

if __name__ == "__main__":
    main()
