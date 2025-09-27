#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FRED API example script that pulls a handful of endpoints,
performs a linear regression between CPI and Unemployment,
and plots the result.
"""

# ------------------------------------------------------------------
#  Import libraries
# ------------------------------------------------------------------
import requests
import pandas as pd

# Optional: use numpy for quick array operations (not required)
import numpy as np

# Regression & plotting
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# ------------------------------------------------------------------
#  API key – make sure this file exists and contains a **valid** key.
#         fred_key = "" or put your key here directly
# ------------------------------------------------------------------
try:
    from fred_key import fred_key          # <-- adjust if you named it differently
except ImportError as exc:                 # pragma: no cover
    raise RuntimeError(
        "Could not import your FRED key.\n"
        "Create a file called `fred_key.py` with:\n\n"
        "    fred_key = \"YOUR_ACTUAL_KEY\"\n"
        "or set the variable directly below."
    ) from exc

# ------------------------------------------------------------------
#  Helper: generic request wrapper that prints a helpful error
# ------------------------------------------------------------------
BASE_URL = "https://api.stlouisfed.org/fred/"

def fred_get(endpoint: str, params: dict) -> requests.Response:
    """Send a GET request to the FRED API and raise on HTTP errors."""
    url = BASE_URL + endpoint
    if "api_key" not in params:
        params["api_key"] = fred_key

    resp = requests.get(url, params=params)
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:      # pragma: no cover
        print(f"\n Request to {url} failed.")
        print("   Status:", resp.status_code)
        print("   Response:", resp.text[:200], "…")  # truncate long responses
        raise exc from None

    return resp


# ------------------------------------------------------------------
#  Pull CPI observations (Monthly, percent change YoY)
# ------------------------------------------------------------------
cpi_series_id = "CPIAUCSL"
start_date = "2000-01-01"
end_date   = "2025-08-31"

cpi_params = {
    "series_id": cpi_series_id,
    "observation_start": start_date,
    "observation_end": end_date,
    "frequency": "m",
    "units": "pc1",          # percent change YoY
    "file_type": "json",
}

cpi_resp   = fred_get("series/observations", cpi_params)
cpi_df     = pd.DataFrame(cpi_resp.json()["observations"])
cpi_df["date"] = pd.to_datetime(cpi_df["date"])
cpi_df.set_index("date", inplace=True)
cpi_df["value"] = cpi_df["value"].astype(float)

print("\n CPI observations YoY% (first 5 rows):")
print(cpi_df.head())


# ------------------------------------------------------------------
#  Pull Unemployment Rate observations (Monthly, linear %)
# ------------------------------------------------------------------
unemp_series_id = "UNRATE"

unemp_params = {
    "series_id": unemp_series_id,
    "observation_start": start_date,
    "observation_end": end_date,
    "frequency": "m",
    "units": "lin",          # linear percent
    "file_type": "json",
}

unemp_resp   = fred_get("series/observations", unemp_params)
unemp_df     = pd.DataFrame(unemp_resp.json()["observations"])
unemp_df["date"] = pd.to_datetime(unemp_df["date"])
unemp_df.set_index("date", inplace=True)
unemp_df["value"] = unemp_df["value"].astype(float)

print("\n Unemployment % observations (first 5 rows):")
print(unemp_df.head())


# ------------------------------------------------------------------
#  Merge the two series on date, drop missing values
# ------------------------------------------------------------------
merged_df = pd.merge(cpi_df, unemp_df, left_index=True, right_index=True,
                     suffixes=("_cpi", "_unemp")).dropna()

# Rename columns for clarity
merged_df.rename(columns={"value_cpi": "CPI YoY %",
                          "value_unemp": "Unemployment %"},
                 inplace=True)

print("\n Merged data (first 5 rows):")
print(merged_df.head())


# ------------------------------------------------------------------
#  Linear regression: Unemployment = a + b * CPI
# ------------------------------------------------------------------
X = merged_df[["CPI YoY %"]].values   # independent variable(s)
y = merged_df["Unemployment %"].values

reg = LinearRegression()
reg.fit(X, y)

a = reg.intercept_
b = reg.coef_[0]
print(f"\nLinear regression result: Unemp = {a:.3f} + {b:.3f} * CPI YoY%")


# ------------------------------------------------------------------
#  Plot the two series and the fitted line
# ------------------------------------------------------------------
plt.figure(figsize=(12, 6))

# Scatter plot of actual data
plt.scatter(merged_df["CPI YoY %"], merged_df["Unemployment %"],
            color="steelblue", alpha=0.7, label="Observed")

# Regression line
x_vals = np.linspace(merged_df["CPI YoY %"].min(),
                     merged_df["CPI YoY %"].max(), 200)
y_pred = reg.predict(x_vals.reshape(-1, 1))
plt.plot(x_vals, y_pred,
         color="darkorange", linewidth=2,
         label=f"Fit: Unemp = {a:.3f} + {b:.3f}·CPI")

# Formatting
plt.title("Unemployment vs. CPI (YoY %) – Linear Regression")
plt.xlabel("CPI YoY %")
plt.ylabel("Unemployment %")
plt.legend()
plt.grid(alpha=0.4)

# Show the plot in a window; comment out if running headless
plt.show()
