#!/usr/bin/env python3
"""Draw docs/grooming/img/ohio_map.png from data/grooming/cases.csv (lat, lon, resolved).
Local only (needs geopandas, matplotlib, shapely). Run after adding a case:
  python3 scripts/grooming/build_map.py"""
import csv, json, os, ssl, urllib.request
import geopandas as gpd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from shapely.geometry import shape
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
cases = list(csv.DictReader(open(os.path.join(ROOT, "data", "grooming", "cases.csv"), encoding="utf-8")))
ctx = ssl.create_default_context()
url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
data = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60, context=ctx))
oh = gpd.GeoDataFrame(geometry=[shape(f["geometry"]) for f in data["features"] if str(f["id"]).startswith("39")], crs="EPSG:4326")
fig, ax = plt.subplots(figsize=(9, 8.2), dpi=200)
oh.boundary.plot(ax=ax, color="#9aa0a6", linewidth=0.6)
oh.plot(ax=ax, color="#f3f4f6", edgecolor="#c9ccd1", linewidth=0.5)
seen = {}
def off(lat, lon):
    key = (round(lat, 1), round(lon, 1)); n = seen.get(key, 0); seen[key] = n + 1
    return lat + (n // 3) * 0.14, lon + (n % 3) * 0.14
RED, BLUE = "#b3261e", "#1f4e9c"
for c in cases:
    if not c.get("lat") or not c.get("lon"): continue
    la, lo = off(float(c["lat"]), float(c["lon"]))
    col = RED if c["resolved"] in ("convicted", "pleaded guilty") else BLUE
    ax.scatter([lo], [la], s=340, c=col, edgecolors="white", linewidths=1.3, zorder=5)
    ax.text(lo, la, c["num"], color="white", ha="center", va="center", fontsize=8.5, fontweight="bold", zorder=6)
for name, la, lo in [("Cleveland", 41.4993, -81.6944), ("Columbus", 39.9612, -82.9988), ("Cincinnati", 39.1031, -84.5120),
                     ("Toledo", 41.6528, -83.5379), ("Dayton", 39.7589, -84.1916), ("Youngstown", 41.0998, -80.6495)]:
    ax.plot(lo, la, marker="s", color="#444", markersize=3, zorder=3)
    ax.annotate(name, (lo, la), xytext=(4, -9), textcoords="offset points", fontsize=7.5, color="#333")
ax.set_xlim(-85.1, -80.3); ax.set_ylim(38.2, 42.1); ax.set_aspect(1 / 0.78); ax.axis("off")
ax.legend(handles=[Patch(facecolor=RED, edgecolor="white", label="Convicted / pleaded guilty"),
                   Patch(facecolor=BLUE, edgecolor="white", label="Charge pending (allegation)")],
          loc="lower left", fontsize=9, frameon=True, framealpha=0.95)
ax.set_title(f"Where Ohio's {len(cases)} Grooming-Charge Cases Were Brought", fontsize=13, fontweight="bold", pad=8)
plt.tight_layout()
out = os.path.join(ROOT, "docs", "grooming", "img", "ohio_map.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
print("map saved", out)
