# ICE Surveillance Contract Dashboard

A data pipeline that pulls contract data from the SAM.gov API and filters
for surveillance-related technology procured by US Immigration and Customs
Enforcement (ICE).

## What this does

1. Pulls all ICE contract notices from the past 12 months via the SAM.gov API
2. Saves the raw data locally as a JSON file
3. Filters for surveillance-related contracts using a keyword list
4. Prints a summary to the terminal

## Setup

### 1. Get a SAM.gov API key
- Go to sam.gov and log in
- Click your name → Profile → scroll to "Public API Key" → Request API Key
- Copy the key — you'll need it in step 3

### 2. Install Python dependencies
```
pip install requests
```

### 3. Add your API key
Open `pull_ice_contracts.py` and replace `YOUR_API_KEY_HERE` with your actual key.

### 4. Run the script
```
python pull_ice_contracts.py
```

## Rate limits

This project is designed for a SAM.gov individual account not associated with
an entity, which has a limit of **10 API requests per 24 hours**. The script
uses at most 8 requests per run, leaving 2 in reserve.

Once data is saved locally, keyword filtering can be re-run unlimited times
without touching the API.

## Output files

| File | Description |
|------|-------------|
| `ice_contracts_raw_YYYY-MM-DD.json` | All ICE contracts, unfiltered |
| `ice_contracts_surveillance_YYYY-MM-DD.json` | Keyword-matched contracts only |

## Collaborating

See CONTRIBUTING.md for how to work on this project with teammates.

## Data sources

- [SAM.gov Contract Opportunities API](https://open.gsa.gov/api/get-opportunities-public-api/)
- [DHS AI Use Case Inventory](https://www.dhs.gov/publication/ai-use-case-inventory-library)
