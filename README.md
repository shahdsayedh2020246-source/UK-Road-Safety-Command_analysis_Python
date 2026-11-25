<div align="center">

# 🛣️ UK Road Safety Command Platform

### See where roads hurt people, and understand why.

An interactive dashboard built from **101,525 police-recorded road collisions** (Great Britain, 2025).
Real map. Danger zones. Area reports. A street-level replay of how collisions happen.

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-data%20cleaning-150458?logo=pandas&logoColor=white)
![Leaflet](https://img.shields.io/badge/Leaflet-real%20map-199900?logo=leaflet&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-vanilla-F7DF1E?logo=javascript&logoColor=black)
![Data](https://img.shields.io/badge/data-UK%20DfT%20STATS19-00703C)
![Status](https://img.shields.io/badge/status-active-2dff8f)

[**Live demo**](https://shahdsayedh2020246-source.github.io/UK-Road-Safety-Command_analysis_Python/) · [**Open in Colab**](https://colab.research.google.com/github/shahdsayedh2020246-source/UK-Road-Safety-Command_analysis_Python/blob/main/UK_Road_Safety_Dashboard.ipynb) · [**Report a bug**](https://github.com/shahdsayedh2020246-source/UK-Road-Safety-Command_analysis_Python/issues)

<!-- Add a hero screenshot or GIF here -->
<!-- ![Dashboard](docs/screenshots/hero.png) -->

</div>

---

## Why this project

Road collisions are not random. Where a road bends, how a junction is laid out, what the speed limit is, whether the street is lit and what the weather is doing all shape where people get hurt.

A few charts and a summary table would not show that. The goal here was a **complete dashboard** you can explore yourself: where the damage concentrates, what the conditions were, and how a crash like that unfolds.

## What it does

| | Feature | What you get |
|---|---|---|
| 🗺️ | **Real interactive map** | Every collision plotted on a zoomable map (Dark, Streets and Satellite views), coloured by severity: fatal, serious, slight |
| 🔴 | **Danger zones** | Pulsing red markers on the 12 most dangerous areas in view, ranked by severity, re-ranked as you zoom and filter |
| 📋 | **Area reports** | Click anywhere for a report: collisions, casualties, a plain-English summary, and how the area compares with the national average (darkness, junctions, high speed, wet roads) |
| 🎬 | **Street-level replay** | An animated reconstruction of a collision from the recorded road type, junction, speed limit, light, weather and road user, including the stopping distance at that speed |
| 🔗 | **Cross-filtering** | Click a bar in any chart and the map, KPIs and every other chart update together |
| 🗂️ | **Four views** | Overview, Road design, Time, Conditions |

<!-- Add screenshots:
![Map](docs/screenshots/map.png)
![Area report](docs/screenshots/area-report.png)
![Street replay](docs/screenshots/street-replay.png)
-->

## Key finding

Collisions away from any junction were the **most severe** in the 2025 data:

| Junction type | Collisions | Fatal or serious |
|---|---:|---:|
| No junction | 45,333 | **28.5%** |
| Private drive | 2,144 | 27.4% |
| 4+ arms | 1,504 | 26.5% |
| Other junction | 6,762 | 25.8% |
| T / staggered | 28,198 | 25.7% |
| Crossroads | 9,456 | 24.4% |

Open roads are faster, so there is less time to react. This is an association in recorded data, not proof of cause. Roundabouts are classified under road type in the 2025 coding, so they are not in this table.

## Data

**Road Safety Data** from the UK Department for Transport (STATS19), 2025:

| File | Rows | Content |
|---|---:|---|
| `dft-road-casualty-statistics-collision-2025.csv` | 101,525 | Location, time, road type, junction, speed limit, light, weather, surface |
| `dft-road-casualty-statistics-vehicle-2025.csv` | 183,948 | Vehicle type, manoeuvre, driver details |
| `dft-road-casualty-statistics-casualty-2025.csv` | 127,883 | Severity, age, pedestrians |

Download from the official page: <https://www.gov.uk/government/statistics/road-safety-data>

> The data files are **not included** in this repository. Download them and place them in the project folder.

## How it works

```
 3 raw CSVs ──► explore ──► clean ──► merge ──► encode ──► build HTML ──► dashboard
```

1. **Explore:** shapes, dtypes, nulls, `-1` codes, value distributions, date and coordinate ranges, table linkage
2. **Clean:** unknown codes (`-1`, `99`) become `Unknown`; dates and times are validated; coordinates are range-checked; the 2025 junction recoding (13, 16, 17) is handled
3. **Merge:** vehicles and casualties are folded into one row per collision (pedestrian, cycle, motorcycle, goods vehicle, bus, car)
4. **Encode:** each collision becomes 18 bytes (14 one-byte columns plus two 16-bit coordinates), base64-encoded into the page. 101,525 collisions fit in about 2.5 MB, so the dashboard is a **single file with no backend**
5. **Render:** vanilla JavaScript draws the points on a canvas over a Leaflet map, recomputes danger zones on every pan, zoom and filter, and animates the street replay

## Quick start

### Option A: run locally

```bash
git clone https://github.com/shahdsayedh2020246-source/UK-Road-Safety-Command_analysis_Python.git
cd UK-Road-Safety-Command_analysis_Python
pip install pandas numpy
```

Put the three CSV files in the same folder, then:

```bash
python clean_and_build.py
```

Open the generated `uk_road_safety_dashboard_live.html` in a browser **while online** (the map tiles load from the internet).

Or just open the hosted version: <https://shahdsayedh2020246-source.github.io/UK-Road-Safety-Command_analysis_Python/>

### Option B: Google Colab

1. Open `UK_Road_Safety_Dashboard.ipynb` in [Colab](https://colab.research.google.com/github/shahdsayedh2020246-source/UK-Road-Safety-Command_analysis_Python/blob/main/UK_Road_Safety_Dashboard.ipynb)
2. Upload the three CSV files to the **Files** panel
3. **Runtime → Run all**
4. The last cell downloads the dashboard

## Repository structure

```
├── clean_and_build.py                 # explore, clean, merge, encode, build
├── template_live.html                 # dashboard template (map, charts, replay)
├── index.html                         # the generated dashboard (served by GitHub Pages)
├── UK_Road_Safety_Dashboard.ipynb     # the same pipeline for Colab
├── land.json                          # optional: coastline outline for the offline template
├── docs/screenshots/                  # images for this README
└── README.md
```

## Tech stack

- **Python:** pandas, NumPy
- **Frontend:** vanilla JavaScript, HTML5 Canvas, CSS
- **Map:** [Leaflet](https://leafletjs.com) with CARTO / OpenStreetMap and Esri tiles

## Limitations

- The **street replay is an illustrative reconstruction.** The police record gives the road layout and conditions, not the exact vehicle paths.
- STATS19 covers **Great Britain** and **police-recorded** collisions, so minor incidents are under-represented.
- The map needs an **internet connection** to load tiles.
- One year of data. Trends over time are not shown yet.

## Roadmap

- [ ] Extend to 1979 to 2025 with DuckDB, and add a trend view
- [ ] Add road-network features from OpenStreetMap (junction density, street layout)
- [ ] Add a risk score per area, adjusted for traffic volume
- [ ] Add export of an area report as PDF

## Credits and licences

- Collision data: **UK Department for Transport**, published under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
- Map data © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors, tiles © [CARTO](https://carto.com/attributions) and Esri
- Coastline outline: [Natural Earth](https://www.naturalearthdata.com) (public domain)
- Code: MIT License (add a `LICENSE` file)

---

<div align="center">

**If this project helped you, give it a ⭐**

</div>
