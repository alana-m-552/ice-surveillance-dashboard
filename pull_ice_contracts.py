import requests
import json
import time
from datetime import datetime, timedelta

# -------------------------------------------------------
# PASTE YOUR SAM.GOV API KEY BETWEEN THE QUOTES BELOW
# -------------------------------------------------------
API_KEY = "SAM-8ec168eb-4e90-41a6-991e-283e20022f53"

# -------------------------------------------------------
# Date range — pulls the last 12 months automatically
# -------------------------------------------------------
today        = datetime.today()
six_months_ago = today - timedelta(days=180)
date_from    = six_months_ago.strftime("%m/%d/%Y")
date_to      = today.strftime("%m/%d/%Y")

print(f"Pulling ICE contracts from {date_from} to {date_to}")
print("=" * 55)

# -------------------------------------------------------
# The broad pull — NO keyword filter
# We ask for ALL ICE contracts, 1000 per page (= 1 request)
# -------------------------------------------------------
BASE_URL = "https://api.sam.gov/prod/opportunities/v2/search"

base_params = {
    "api_key":     API_KEY,
    "deptname":    "HOMELAND SECURITY, DEPARTMENT OF",
    "subtierName": "US IMMIGRATION AND CUSTOMS ENFORCEMENT",
    "postedFrom":  date_from,
    "postedTo":    date_to,
    "limit":       "1000",
}

all_contracts = []
page = 0
requests_used = 0

while True:
    params = base_params.copy()
    params["offset"] = str(page * 1000)

    print(f"\nRequest {requests_used + 1}: fetching records {page*1000} to {page*1000 + 1000}...")

    response = requests.get(BASE_URL, params=params)
    requests_used += 1

    if response.status_code != 200:
        print(f"ERROR {response.status_code}: {response.text[:500]}")
        break

    data          = response.json()
    total_records = data.get("totalRecords", 0)
    fetched       = data.get("opportunitiesData", [])

    print(f"  Total matching records on SAM.gov: {total_records}")
    print(f"  Records retrieved this request:    {len(fetched)}")

    all_contracts.extend(fetched)

    # Stop at 8 requests — leaves 2 spare from your daily 10
    if requests_used >= 8:
        print("\nStopping: used 8 of 10 daily requests (holding 2 in reserve).")
        break

    if len(all_contracts) >= total_records:
        print("  All records retrieved.")
        break

    page += 1
    print("  Pausing 2 seconds...")
    time.sleep(2)

print(f"\n{'='*55}")
print(f"TOTAL CONTRACTS DOWNLOADED: {len(all_contracts)}")
print(f"API REQUESTS USED:          {requests_used} of 10")

# -------------------------------------------------------
# Save raw data locally — reuse this file all day without
# spending any more API requests
# -------------------------------------------------------
raw_file = f"ice_contracts_raw_{today.strftime('%Y-%m-%d')}.json"
with open(raw_file, "w") as f:
    json.dump(all_contracts, f, indent=2)
print(f"\nRaw data saved to: {raw_file}")

# -------------------------------------------------------
# LOCAL keyword filtering — costs ZERO API requests
# Edit this list freely and re-run as many times as you want
# -------------------------------------------------------
SURVEILLANCE_KEYWORDS = [
    "surveillance",
    "biometric",
    "facial recognition",
    "face recognition",
    "license plate",
    "monitoring",
    "detection system",
    "analytics platform",
    "intelligence platform",
    "tracking",
    "identification system",
    "geospatial",
    "video analysis",
    "social media",
    "open source intelligence",
    "OSINT",
    "predictive",
    "risk scoring",
    "data analytics",
    "investigative",
    "Palantir",
    "Clearview",
    "Babel Street",
    "Cellebrite",
    "IDEMIA",
    "RAVEn",
    "ELITE",
    "HSI",
]

print(f"\n{'='*55}")
print("FILTERING LOCALLY (no API requests used)...")

matched_contracts = []

for contract in all_contracts:
    title       = (contract.get("title") or "").lower()
    description = (contract.get("description") or "").lower()
    searchable  = title + " " + description

    matched_keywords = [kw for kw in SURVEILLANCE_KEYWORDS if kw.lower() in searchable]

    if matched_keywords:
        contract["_matched_keywords"] = matched_keywords
        matched_contracts.append(contract)

print(f"Contracts matching at least one keyword: {len(matched_contracts)}")

# -------------------------------------------------------
# Save filtered results
# -------------------------------------------------------
filtered_file = f"ice_contracts_surveillance_{today.strftime('%Y-%m-%d')}.json"
with open(filtered_file, "w") as f:
    json.dump(matched_contracts, f, indent=2)
print(f"Filtered results saved to: {filtered_file}")

# -------------------------------------------------------
# Print a readable summary to the terminal
# -------------------------------------------------------
print(f"\n{'='*55}")
print("MATCHED CONTRACTS — SUMMARY")
print(f"{'='*55}\n")

for i, c in enumerate(matched_contracts, 1):
    title    = c.get("title", "No title")
    vendor   = c.get("award", {}).get("awardee", {}).get("name", "Unknown vendor")
    amount   = c.get("award", {}).get("amount", "N/A")
    posted   = c.get("postedDate", "N/A")
    keywords = ", ".join(c.get("_matched_keywords", []))

    print(f"{i}. {title}")
    print(f"   Vendor:   {vendor}")
    print(f"   Amount:   ${amount}")
    print(f"   Posted:   {posted}")
    print(f"   Keywords: {keywords}")
    print()

print("Done.")
