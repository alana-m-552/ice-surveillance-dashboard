import requests
import json
import time
from datetime import datetime, timedelta

# -------------------------------------------------------
# PASTE YOUR SAM.GOV API KEY BETWEEN THE QUOTES BELOW
# Same key you used in the original script
# -------------------------------------------------------
API_KEY = "SAM-91ccd717-7373-4f42-89bf-61b6fe74e966"

# -------------------------------------------------------
# Date range — 180 days (SAM.gov rejects ranges over ~1 year)
# -------------------------------------------------------
today             = datetime.today()
twelve_months_ago = today - timedelta(days=360)
six_months_ago    = today - timedelta(days=180)
date_from         = twelve_months_ago.strftime("%m/%d/%Y")
date_to           = six_months_ago.strftime("%m/%d/%Y")

print("=" * 55)
print("ICE ACTIVE AWARD NOTICES PULL")
print("=" * 55)
print(f"Date range:  {date_from}  →  {date_to}")
print(f"Notice type: Award notices only (ptype=a)")
print(f"Status:      Active contracts only (active=true)")
print("=" * 55)

BASE_URL = "https://api.sam.gov/prod/opportunities/v2/search"

# -------------------------------------------------------
# KEY DIFFERENCE from the original script:
#   ptype  = "a"     → award notices only (vendor was chosen,
#                       contract was signed)
#   active = "true"  → only contracts currently active
#                       (not expired, not cancelled)
# -------------------------------------------------------
base_params = {
    "api_key":     API_KEY,
    "deptname":    "HOMELAND SECURITY, DEPARTMENT OF",
    "subtierName": "US IMMIGRATION AND CUSTOMS ENFORCEMENT",
    "postedFrom":  date_from,
    "postedTo":    date_to,
    "ptype":       "a",        # Award notices only
    "active":      "true",     # Active contracts only
    "limit":       "1000",
}

active_awards = []
page          = 0
requests_used = 0

while True:
    params           = base_params.copy()
    params["offset"] = str(page * 1000)

    print(f"\nRequest {requests_used + 1}: fetching records {page*1000} to {page*1000 + 1000}...")

    response      = requests.get(BASE_URL, params=params)
    requests_used += 1

    if response.status_code != 200:
        print(f"ERROR {response.status_code}: {response.text[:500]}")
        break

    data          = response.json()
    total_records = data.get("totalRecords", 0)
    fetched       = data.get("opportunitiesData", [])

    print(f"  Total active award notices on SAM.gov: {total_records}")
    print(f"  Records retrieved this request:        {len(fetched)}")

    active_awards.extend(fetched)

    # Stop at 8 requests — keeps 2 in reserve from your daily 10
    if requests_used >= 8:
        print("\nStopping: used 8 of 10 daily requests (holding 2 in reserve).")
        break

    if len(active_awards) >= total_records:
        print("  All records retrieved.")
        break

    page += 1
    print("  Pausing 2 seconds before next request...")
    time.sleep(2)

print(f"\n{'='*55}")
print(f"TOTAL ACTIVE AWARD NOTICES DOWNLOADED: {len(active_awards)}")
print(f"API REQUESTS USED:                     {requests_used} of 10")

# -------------------------------------------------------
# Save to a clearly named new file — completely separate
# from ice_contracts_raw_*.json
# -------------------------------------------------------
output_file = f"ice_active_awards_{today.strftime('%Y-%m-%d')}.json"
with open(output_file, "w") as f:
    json.dump(active_awards, f, indent=2)

print(f"\nSaved to: {output_file}")
print("(Your original ice_contracts_raw file is untouched.)")

# -------------------------------------------------------
# LOCAL keyword filtering — zero API requests
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

matched = []

for contract in active_awards:
    title       = (contract.get("title") or "").lower()
    description = (contract.get("description") or "").lower()
    searchable  = title + " " + description

    matched_keywords = [kw for kw in SURVEILLANCE_KEYWORDS if kw.lower() in searchable]

    if matched_keywords:
        contract["_matched_keywords"] = matched_keywords
        matched.append(contract)

print(f"Active award notices matching surveillance keywords: {len(matched)}")

# -------------------------------------------------------
# Save the filtered active awards to its own file
# -------------------------------------------------------
filtered_file = f"ice_active_awards_surveillance_{today.strftime('%Y-%m-%d')}.json"
with open(filtered_file, "w") as f:
    json.dump(matched, f, indent=2)

print(f"Filtered results saved to: {filtered_file}")

# -------------------------------------------------------
# Print a human-readable summary
# -------------------------------------------------------
print(f"\n{'='*55}")
print("ACTIVE SURVEILLANCE CONTRACTS — SUMMARY")
print(f"{'='*55}\n")

if not matched:
    print("No matches found. Try expanding the date range or keyword list.")
else:
    for i, c in enumerate(matched, 1):
        title    = c.get("title", "No title")
        vendor   = c.get("award", {}).get("awardee", {}).get("name", "Unknown vendor")
        amount   = c.get("award", {}).get("amount", "N/A")
        posted   = c.get("postedDate", "N/A")
        sol_num  = c.get("solicitationNumber", "N/A")
        keywords = ", ".join(c.get("_matched_keywords", []))

        print(f"{i}. {title}")
        print(f"   Vendor:        {vendor}")
        print(f"   Amount:        ${amount}")
        print(f"   Award posted:  {posted}")
        print(f"   Contract #:    {sol_num}")
        print(f"   Keywords:      {keywords}")
        print()

print(f"Files written:")
print(f"  All active awards:           {output_file}")
print(f"  Surveillance matches only:   {filtered_file}")
print(f"  Original broad pull:         ice_contracts_raw_*.json  (untouched)")