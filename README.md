# ICE Surveillance Contract Dashboard

A data pipeline that pulls contract data from the SAM.gov API and filters
for surveillance-related technology procured by US Immigration and Customs
Enforcement (ICE).

## What this does

1. Pulls all ICE contract notices from the past 6 months via the SAM.gov API
2. Saves the raw data locally as a JSON file
3. Filters for surveillance-related contracts using a keyword list
4. Prints a summary to the terminal

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


## Data sources

- [SAM.gov Contract Opportunities API](https://open.gsa.gov/api/get-opportunities-public-api/)
- [DHS AI Use Case Inventory](https://www.dhs.gov/publication/ai-use-case-inventory-library)
