#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FRED API – example script that pulls a handful of endpoints.
The original version kept producing “Status code 400”.
This rewrite addresses the most frequent causes:
    * missing or wrong API key
    * malformed URLs / endpoint names
    * missing required query parameters
    * typo in JSON keys when building DataFrames

Author: Adam Getbags (modified by ChatGPT)
"""

# ----------------------------------------------------------------------
# 1️⃣  Imports
# ----------------------------------------------------------------------
import requests
import pandas as pd

# ----------------------------------------------------------------------
# 2️⃣  API key – make sure this file exists and contains a **valid** key.
#     The file should simply contain the key, e.g.:
#         fred_key = "abcdefg1234567890"
# ----------------------------------------------------------------------
try:
    from fred_key import fred_key          # <-- adjust if you named it differently
except ImportError as exc:                 # pragma: no cover
    raise RuntimeError(
        "Could not import your FRED key.\n"
        "Create a file called `fred_key.py` with:\n\n"
        "    fred_key = \"YOUR_ACTUAL_KEY\"\n"
        "or set the variable directly below."
    ) from exc

# ----------------------------------------------------------------------
# 3️⃣  Base URL – keep it exactly as documented
# ----------------------------------------------------------------------
BASE_URL = "https://api.stlouisfed.org/fred/"

# ----------------------------------------------------------------------
# 4️⃣  Helper: generic request wrapper that prints a helpful error
# ----------------------------------------------------------------------
def fred_get(endpoint: str, params: dict) -> requests.Response:
    """Send a GET request to the FRED API and raise on HTTP errors."""
    url = BASE_URL + endpoint
    # Every request must include your key – no one else will know it!
    if "api_key" not in params:
        params["api_key"] = fred_key

    resp = requests.get(url, params=params)
    try:
        resp.raise_for_status()            # raises for 4xx/5xx
    except requests.HTTPError as exc:      # pragma: no cover
        print(f"\n❌ Request to {url} failed.")
        print("   Status:", resp.status_code)
        print("   Response:", resp.text[:200], "…")  # truncate long responses
        raise exc from None

    return resp

# ----------------------------------------------------------------------
# 5️⃣  Example: Pull CPI observations (Monthly, percent change)
# ----------------------------------------------------------------------
series_id = "CPIAUCSL"
start_date = "2000-01-01"
end_date   = "2025-08-31"

obs_params = {
    "series_id": series_id,
    "observation_start": start_date,
    "observation_end": end_date,
    # The following *are optional* but help you get the data you want
    "frequency": "m",          # monthly – required if you want a specific period
    "units": "pc1",            # percent change (year‑over‑year)
    "file_type": "json",
}

response = fred_get("series/observations", obs_params)
obs_data = pd.DataFrame(response.json()["observations"])
obs_data["date"] = pd.to_datetime(obs_data["date"])
obs_data.set_index("date", inplace=True)
obs_data["value"] = obs_data["value"].astype(float)

print("\n✅ CPI observations YoY% (first 5 rows):")
print(obs_data.head())

# ----------------------------------------------------------------------
# 5️⃣  Example: Pull Unemployment Rate observations (Monthly)
# ----------------------------------------------------------------------
series_id = "UNRATE"
start_date = "2000-01-01"
end_date   = "2025-08-31"

obs_params = {
    "series_id": series_id,
    "observation_start": start_date,
    "observation_end": end_date,
    # The following *are optional* but help you get the data you want
    "frequency": "m",          # monthly – required if you want a specific period
    "units": "lin",            # percent change (year‑over‑year)
    "file_type": "json",
}

response = fred_get("series/observations", obs_params)
obs_data = pd.DataFrame(response.json()["observations"])
obs_data["date"] = pd.to_datetime(obs_data["date"])
obs_data.set_index("date", inplace=True)
obs_data["value"] = obs_data["value"].astype(float)

print("\n✅ Unemployment % observations (first 5 rows):")
print(obs_data.head())


'''
# ----------------------------------------------------------------------
# 6️⃣  Example: List all releases
# ----------------------------------------------------------------------
rel_params = {"file_type": "json"}
response = fred_get("releases", rel_params)
rel_df = pd.DataFrame(response.json()["releases"])
print("\n✅ Release IDs & names:")
print(rel_df[["id", "name"]].head())

# ----------------------------------------------------------------------
# 7️⃣  Example: Get series for a specific release
# ----------------------------------------------------------------------
release_id = 10   # e.g., “Economic Indicators” – change if you want another
rel_series_params = {
    "release_id": release_id,
    "file_type": "json",
}
response = fred_get("release/series", rel_series_params)
rel_srs_df = pd.DataFrame(response.json()["seriess"])
print(f"\n✅ Series for release {release_id} (first 5 rows):")
print(rel_srs_df[["id", "title"]].head())
'''