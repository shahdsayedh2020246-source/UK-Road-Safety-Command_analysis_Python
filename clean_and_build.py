"""UK STATS19 road safety: clean -> merge -> encode -> build interactive dashboard.
Usage: python clean_and_build.py   (edit DIR / TEMPLATE / OUT below)"""
import pandas as pd, numpy as np, base64, json, os
HERE = os.path.dirname(os.path.abspath(__file__))

DIR = HERE            # folder with the 3 STATS19 CSV files (change if they are elsewhere)
TEMPLATE = HERE + '/template_live.html'
LAND = HERE + '/land.json'
OUT = HERE + '/uk_road_safety_dashboard_live.html'
U = DIR + '/dft-road-casualty-statistics-%s-2025.csv'

# ---------- 1) Load ----------
c = pd.read_csv(U % 'collision', low_memory=False)
v = pd.read_csv(U % 'vehicle', usecols=['collision_index', 'vehicle_type'])
k = pd.read_csv(U % 'casualty', usecols=['collision_index', 'casualty_class'])
print('rows loaded  collisions/vehicles/casualties:', len(c), len(v), len(k))

# ---------- 2) Clean ----------
n0 = len(c)
c = c.drop_duplicates('collision_index').reset_index(drop=True)
print('duplicate collisions removed:', n0 - len(c))

# code -> label (from the DfT data guide). Anything else (-1, 99, 9...) becomes "Unknown"
D = {
 'sev': ('collision_severity', {1: 'Fatal', 2: 'Serious', 3: 'Slight'}),
 'rt': ('road_type', {1: 'Roundabout', 2: 'One way street', 3: 'Dual carriageway', 6: 'Single carriageway', 7: 'Slip road', 12: 'One way / slip road'}),
 'jn': ('junction_detail', {0: 'No junction', 13: 'T / staggered', 16: 'Crossroads', 17: '4+ arms', 18: 'Private drive', 19: 'Other junction'}),
 'sp': ('speed_limit', {20: '20 mph', 30: '30 mph', 40: '40 mph', 50: '50 mph', 60: '60 mph', 70: '70 mph'}),
 'li': ('light_conditions', {1: 'Daylight', 4: 'Dark, lit', 5: 'Dark, unlit', 6: 'Dark, no lighting', 7: 'Dark, unknown'}),
 'we': ('weather_conditions', {1: 'Fine', 2: 'Rain', 3: 'Snow', 4: 'Fine + wind', 5: 'Rain + wind', 6: 'Snow + wind', 7: 'Fog / mist', 8: 'Other'}),
 'su': ('road_surface_conditions', {1: 'Dry', 2: 'Wet / damp', 3: 'Snow', 4: 'Frost / ice', 5: 'Flood', 6: 'Oil / diesel', 7: 'Mud'}),
 'ur': ('urban_or_rural_area', {1: 'Urban', 2: 'Rural'}),
}
cols, names = {}, {}
for key, (col, mp) in D.items():
    lab = list(mp.values()) + ['Unknown']
    idx = {code: i for i, code in enumerate(mp)}
    unk = (~c[col].isin(mp.keys())).sum()
    print(f'{col:26s} unknown/-1 -> "Unknown": {unk}')
    cols[key] = c[col].map(idx).fillna(len(lab) - 1).astype(int)
    names[key] = lab

# dates / times
dt = pd.to_datetime(c['date'], format='%d/%m/%Y', errors='coerce')
tm = pd.to_datetime(c['time'], format='%H:%M', errors='coerce')
print('bad dates:', dt.isna().sum(), '| bad times:', tm.isna().sum())
cols['dow'] = dt.dt.dayofweek.fillna(0).astype(int)
cols['mo'] = (dt.dt.month.fillna(1) - 1).astype(int)
cols['hr'] = tm.dt.hour.fillna(0).astype(int)

# ---------- 3) Merge vehicles + casualties into one row per collision ----------
ped = set(k.loc[k.casualty_class == 3, 'collision_index'])
grp = lambda ts: set(v.loc[v.vehicle_type.isin(ts), 'collision_index'])
cyc, mot = grp([1]), grp([2, 3, 4, 5, 23, 97, 103, 104, 105, 106])
gds, bus = grp([19, 20, 21, 98, 113]), grp([10, 11, 108, 109])
ci = c['collision_index']
cols['inv'] = np.select([ci.isin(ped), ci.isin(cyc), ci.isin(mot), ci.isin(gds), ci.isin(bus)], [0, 1, 2, 3, 4], 5)
names['inv'] = ['Pedestrian', 'Pedal cycle', 'Motorcycle', 'Van / goods', 'Bus / coach', 'Cars & other']
cols['cas'] = c['number_of_casualties'].clip(0, 255)
cols['veh'] = c['number_of_vehicles'].clip(0, 255)

# ---------- 4) Coordinates ----------
ok = c.latitude.between(49.8, 61) & c.longitude.between(-8.7, 2)
print('missing / out-of-range coordinates (kept in charts, hidden on map):', (~ok).sum())
la = np.where(ok, ((c.latitude - 49.5) / 11.5 * 65535).round(), 0).astype('<u2')
lo = np.where(ok, ((c.longitude + 9) / 11 * 65535).round(), 0).astype('<u2')

# ---------- 5) Quick analysis printout ----------
print('\nFatal+serious share by junction type:')
t = pd.DataFrame({'jn': [names['jn'][i] for i in cols['jn']], 'ks': np.array(cols['sev']) < 2})
print((t.groupby('jn').ks.agg(['mean', 'size']).round(3)).sort_values('mean', ascending=False).to_string())

# ---------- 6) Encode + build ----------
ORDER = ['sev', 'dow', 'hr', 'mo', 'rt', 'jn', 'sp', 'li', 'we', 'su', 'ur', 'inv', 'cas', 'veh']
buf = b''.join(np.asarray(cols[x]).astype('u1').tobytes() for x in ORDER) + la.tobytes() + lo.tobytes()
meta = {x: names[x] for x in names}
html = open(TEMPLATE, encoding='utf-8').read()
html = html.replace('__DATA__', base64.b64encode(buf).decode()).replace('__N__', str(len(c))).replace('__META__', json.dumps(meta)).replace('__LAND__', open(LAND).read() if os.path.exists(LAND) else '[]')
open(OUT, 'w', encoding='utf-8').write(html)
print(f'\nBuilt {OUT}  ({len(html)/1e6:.2f} MB, {len(c):,} collisions)')
