#!/usr/bin/env python3
"""Rebuild the two SVG figures in ../assets from the data in this folder.

Python 3, standard library only. Run from any directory:
    python data/build_figures.py
"""
from pathlib import Path
import csv
import json
from html import escape

D = Path(__file__).resolve().parent
A = D.parent / 'assets'
A.mkdir(exist_ok=True)

INK = '#202428'
LINE = '#6f757b'
FONT = 'Arial, Helvetica, sans-serif'
REGION = {  # fill, stroke
    'CN': ('#fbefdf', '#b7783d'),
    'US': ('#edf3fa', '#4b749b'),
    'FR': ('#f0eef5', '#777087'),
    'MIX': ('#ffffff', '#8a8f94'),
}
BAR = {'china': '#e6bc91', 'us': '#a9bfd5', 'other_unknown': '#e5e5e8'}


def start(w, h, title, desc, metadata):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        'role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>',
        '<metadata>' + escape(json.dumps(metadata, ensure_ascii=False)) + '</metadata>',
        '<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto" '
        'markerUnits="userSpaceOnUse"><path d="M0,0 L7,3.5 L0,7" fill="none" stroke="#6f757b" '
        'stroke-width="1.4"/></marker></defs>',
        f'<rect width="{w}" height="{h}" fill="white"/>',
        f'<g font-family="{FONT}" fill="{INK}">',
    ]


def text(s, x, y, t, size=18, weight=400, anchor='start', fill=INK, style=None):
    st = f' font-style="{style}"' if style else ''
    s.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
             f'text-anchor="{anchor}" fill="{fill}"{st}>{escape(str(t))}</text>')


def arrow(s, d, ids=None):
    attr = f' data-source-edges="{escape(ids)}"' if ids else ''
    s.append(f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="1.5" '
             f'stroke-linejoin="round" marker-end="url(#arrow)"{attr}/>')


def box(s, x, y, w, h, region, node_id):
    fill, stroke = REGION[region]
    s.append(f'<g id="{node_id}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" '
             f'fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>')
    return stroke


def single(s, x, y, w, h, region, name, node_id, size=18):
    """One artifact: country tag at the left, name beside it."""
    stroke = box(s, x, y, w, h, region, node_id)
    text(s, x + 8, y + h / 2 + 6, region, 15, 700, fill=stroke)
    text(s, x + 40, y + h / 2 + 6, name, size)
    s.append('</g>')


def group(s, x, y, w, region, names, node_id, size=18, tags=None):
    """Several artifacts that play the same role. One tag per line if tags is given,
    otherwise one tag for the box."""
    h = 22 + 24 * len(names) + 6
    stroke = box(s, x, y, w, h, region, node_id)
    if tags is None:
        text(s, x + 8, y + 17, region, 15, 700, fill=stroke)
    yy = y + 40
    for i, n in enumerate(names):
        text(s, x + 10, yy + i * 24, n, size)
        if tags is not None:
            t = tags[i]
            text(s, x + w - 8, yy + i * 24, t, 15, 700, anchor='end', fill=REGION[t][1])
    s.append('</g>')
    return h


# ---------------------------------------------------------------- Figure 1: census
rows = list(csv.DictReader((D / 'census-by-relation.csv').open()))
meta = json.loads((D / 'census-totals.json').read_text())
s = start(720, 452,
          'Chinese-released models appear most often where training data was generated',
          'Four rows compare releasing organizations across documented relationship types in the '
          'combined histories of seven open releases. Generated training data: China 173, United '
          'States 128, other or unknown 35, total 336. Filtered, rewrote, or embedded data: 45, 88, '
          '21, total 154. Weight lineage: 12, 48, 4, total 64. Training datasets: 77, 848, 215, '
          'total 1,140. Counts are documented relationships, not tokens.', meta)
text(s, 12, 27, 'Seven releases · documented relationships, by releasing organization', 21, 600)
for x, key, label in [(12, 'china', 'China'), (150, 'us', 'United States'), (375, 'other_unknown', 'Other / unknown')]:
    s.append(f'<rect x="{x}" y="43" width="21" height="17" fill="{BAR[key]}" stroke="{LINE}" stroke-width=".8"/>')
    text(s, x + 29, 59, label, 20)
labels = ['Generated the training data', 'Filtered, rewrote, or embedded the data',
          'Weight lineage', 'Training datasets']
for i, r in enumerate(rows):
    y = 96 + i * 86
    n = int(r['total'])
    cn = int(r['china'])
    pct = f'{cn / n * 100:.1f}'
    text(s, 12, y, f'{labels[i]} · {n:,}', 21, 600)
    text(s, 708, y, f'{pct}% China', 21, 600, anchor='end')
    x = 12
    for k in ['china', 'us', 'other_unknown']:
        v = int(r[k])
        w = 696 * v / n
        s.append(f'<rect x="{x:.3f}" y="{y + 13}" width="{w:.3f}" height="33" fill="{BAR[k]}" '
                 f'stroke="white" stroke-width="1"/>')
        if w > 34:
            text(s, x + w / 2, y + 37, f'{v:,}', 20, anchor='middle')
        x += w
    s.append(f'<rect x="12" y="{y + 13}" width="696" height="33" fill="none" stroke="{LINE}" stroke-width=".9"/>')
text(s, 12, 437, 'Weight lineage: initialized, merged, or quantized from a model. One relationship is one edge.', 17)
s += ['</g></svg>']
(A / 'census.svg').write_text('\n'.join(s) + '\n')

# ---------------------------------------------------------------- Figure 2: the LIMO relay
fig = json.loads((D / 'limo-source-edges.json').read_text())
s = start(760, 392,
          'The LIMO relay: American problem sets, Chinese curation, an American release',
          'Left: problem sets AIME, MATH, and DeepScaleR (United States) and NuminaMath-CoT (France) '
          'supply problems to the LIMO dataset (China). Middle: Qwen2.5-Math-7B-Instruct and '
          'DeepSeek-R1-Distill-Qwen-32B filter the problems; DeepSeek-R1, DeepSeek-R1-Distill-Qwen-32B, '
          'and QwQ-32B generate solutions. Right: NVIDIA uses LIMO as the seed and DeepSeek-R1-0528 '
          '(China) to regenerate solutions for Nemotron 3 Super Base and Nano Base (United States); '
          'Super Base is post-trained into Nemotron 3 Super. Box color and tag give the country of the '
          'releasing organization.', fig)

# Column bands and headers.
for x, w, head in [(4, 190, 'Problem sets'), (238, 252, 'LIMO curation, Shanghai'), (526, 230, 'Nemotron 3, NVIDIA')]:
    s.append(f'<rect x="{x}" y="6" width="{w}" height="352" rx="6" fill="#f7f7f8"/>')
    text(s, x + 8, 28, head, 19, 700)

# Column 1: the four problem sets in one box, one country tag per line.
group(s, 10, 110, 178, 'MIX', ['AIME', 'MATH', 'DeepScaleR', 'NuminaMath-CoT'], 'sources',
      tags=['US', 'US', 'US', 'FR'], size=17)
# Column 2: filters, the LIMO dataset, generators.
group(s, 246, 40, 236, 'CN', ['Qwen2.5-Math-7B-Instruct', 'R1-Distill-Qwen-32B'], 'filters')
box(s, 246, 156, 236, 52, 'CN', 'limo-dataset')
text(s, 254, 187, 'CN', 15, 700, fill=REGION['CN'][1])
text(s, 286, 178, 'LIMO dataset', 18, 600)
text(s, 286, 200, '817 solved problems', 16)
s.append('</g>')
group(s, 246, 254, 236, 'CN', ['DeepSeek-R1', 'R1-Distill-Qwen-32B', 'QwQ-32B'], 'generators')
# Column 3: the generator NVIDIA applied, the two base models, the post-trained release.
single(s, 534, 40, 214, 36, 'CN', 'DeepSeek-R1-0528', 'r1-0528')
group(s, 534, 140, 214, 'US', ['Nemotron 3 Super Base', 'Nemotron 3 Nano Base'], 'nemotron-base')
single(s, 534, 280, 214, 36, 'US', 'Nemotron 3 Super', 'nemotron-super')

# Edges, supplier -> user, labeled with the operation.
arrow(s, 'M188 182 H244', 'E04 E05 E06 E07')
text(s, 216, 172, 'problems', 14, anchor='middle')
arrow(s, 'M364 118 V154')
text(s, 372, 141, 'filter', 15)
arrow(s, 'M364 254 V212')
text(s, 372, 240, 'generate solutions', 15)
arrow(s, 'M482 182 H532', 'E01 E03')
text(s, 507, 172, 'seed', 15, anchor='middle')
arrow(s, 'M700 76 V138')
text(s, 692, 112, 'regenerate solutions', 15, anchor='end')
arrow(s, 'M641 218 V278', 'E02')
text(s, 650, 254, 'post-train', 15)

text(s, 8, 378, 'Tag and color: country of the releasing organization. R1-Distill-Qwen-32B appears in two roles.', 14)
s += ['</g></svg>']
(A / 'limo-relay.svg').write_text('\n'.join(s) + '\n')
print('Built', A / 'census.svg', 'and', A / 'limo-relay.svg')

# ---------------------------------------------------------------- Figure 3: generators by release quarter
gens = list(csv.DictReader((D / 'generators-by-release.csv').open()))
quarters = [f'{y}Q{q}' for y in (2023, 2024, 2025) for q in (1, 2, 3, 4)] + ['2026Q1']
stack = {q: {'china': 0, 'us': 0, 'eu': 0, 'other': 0} for q in quarters}
KEY = {'CN': 'china', 'US': 'us', 'EU': 'eu', 'OTHER': 'other'}
for g in gens:
    if not g['release_month']:
        continue
    y, m = g['release_month'].split('-')
    q = f"{y}Q{(int(m) - 1) // 3 + 1}"
    if q in stack:
        stack[q][KEY.get(g['region'], 'other')] += int(g['edges'])
BAR2 = dict(BAR, eu='#c9c3d9', other='#e5e5e8')
pre = {k: sum(stack[q][k] for q in quarters[:6]) for k in ('china', 'us', 'eu', 'other')}
post = {k: sum(stack[q][k] for q in quarters[6:]) for k in ('china', 'us', 'eu', 'other')}
s = start(720, 420,
          'Generators in the census by the quarter the generator was released',
          'Stacked bars by release quarter from 2023 to early 2026, counting the 336 documented '
          'data-generation relationships by the country of the generating model. Among generators '
          f"released before July 2024, {pre['china']} of {sum(pre.values())} relationships name a Chinese model; "
          f"among generators released since, {post['china']} of {sum(post.values())}.", {'source': 'generators-by-release.csv'})
text(s, 12, 27, "Data-generation relationships by generator release quarter", 21, 600)
for x, key, label in [(12, 'china', 'China'), (110, 'us', 'United States'), (270, 'eu', 'EU'), (340, 'other', 'Other')]:
    s.append(f'<rect x="{x}" y="43" width="21" height="17" fill="{BAR2[key]}" stroke="{LINE}" stroke-width=".8"/>')
    text(s, x + 29, 59, label, 19)
text(s, 12, 84, f"Generators released before July 2024: Chinese in {pre['china']} of {sum(pre.values())} relationships. "
     f"Since: {post['china']} of {sum(post.values())}.", 15)
x0, y0, w, h = 24, 100, 684, 250   # plot area
scale = 2.2
bw = w / len(quarters)
def bx(i): return x0 + i * bw + 5
base = y0 + h
for i, q in enumerate(quarters):
    x = bx(i)
    y = base
    for key in ('china', 'us', 'eu', 'other'):
        v = stack[q][key]
        if not v:
            continue
        hh = v * scale
        y -= hh
        s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw - 10:.1f}" height="{hh:.1f}" fill="{BAR2[key]}" stroke="white" stroke-width="1"/>')
        if hh > 15:
            text(s, x + (bw - 10) / 2, y + hh / 2 + 6, str(v), 16, anchor='middle')
    if q.endswith('Q1'):
        text(s, x + (bw - 10) / 2, base + 18, q[:4], 15, anchor='middle')
    text(s, x + (bw - 10) / 2, base + 34, 'Q' + q[-1], 13, anchor='middle', fill=LINE)
s.append(f'<line x1="{x0}" y1="{base}" x2="{x0 + w}" y2="{base}" stroke="{LINE}" stroke-width="1"/>')
def note(qi, txt, dy=8):
    x = bx(qi) + (bw - 10) / 2
    top = base - sum(stack[quarters[qi]].values()) * scale
    text(s, x, top - dy, txt, 13, anchor='middle')
note(0, 'GPT-4')
note(3, 'Mixtral')
note(5, 'GPT-4o · Nemotron-4')
note(6, 'Qwen2.5', 28)
note(8, 'R1 · QwQ')
note(9, 'Qwen3 · R1-0528')
note(10, 'gpt-oss · K2')
xd = x0 + 6 * bw
s.append(f'<line x1="{xd:.1f}" y1="{y0 + 10}" x2="{xd:.1f}" y2="{base}" stroke="{LINE}" stroke-width="1" stroke-dasharray="4 4"/>')
text(s, xd - 6, y0 + 22, 'July 2024', 13, anchor='end', fill=LINE)
text(s, 12, 408, "One relationship is one documented edge. The quarter is the generating model's release, not the dataset's.", 14)
s += ['</g></svg>']
(A / 'generators-by-quarter.svg').write_text('\n'.join(s) + '\n')

# ---------------------------------------------------------------- Figure 4: disclosure trend
disc = list(csv.DictReader((D / 'disclosure-trend.csv').open()))
series = {}
for r in disc:
    series.setdefault(r['attribute'], {})[r['period']] = float(r['download_weighted_percent'])
periods = ['≤2022', '2023', '2024', '2025*']
plabels = ['through 2022', '2023', '2024', '2025']
s = start(720, 320,
          'Downloaded models disclose less of their training data each year',
          'Two lines over four periods, download-weighted. Training data disclosed and available falls '
          'from 79.3 to 58.5 to 53.5 to 39.8 percent; training data not disclosed rises from 9.8 to '
          '23.4 to 31.6 to 43.1 percent.', {'source': 'disclosure-trend.csv'})
text(s, 12, 27, 'Training-data disclosure, download-weighted share of models', 21, 600)
SER = [('Data disclosed & available', 'Training data disclosed and available', '#4b749b'),
       ('Data not disclosed', 'Training data not disclosed', '#b7783d')]
lx = 12
for key, name, color in SER:
    s.append(f'<line x1="{lx}" y1="51" x2="{lx + 26}" y2="51" stroke="{color}" stroke-width="2.2"/>')
    s.append(f'<circle cx="{lx + 13}" cy="51" r="4" fill="{color}"/>')
    text(s, lx + 34, 56, name, 17)
    lx += 34 + len(name) * 8.6 + 24
x0, y0, w, h = 66, 78, 630, 180
def X(i): return x0 + i * w / 3
def Y(v): return y0 + h - v / 100 * h
for v in (0, 25, 50, 75, 100):
    s.append(f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x0 + w}" y2="{Y(v):.1f}" stroke="#e4e4e6" stroke-width="1"/>')
    text(s, x0 - 8, Y(v) + 5, f'{v}%', 13, anchor='end', fill=LINE)
for i, pl in enumerate(plabels):
    text(s, X(i), y0 + h + 22, pl, 15, anchor='middle')
for key, name, color in SER:
    pts = [(X(i), Y(series[key][pp])) for i, pp in enumerate(periods)]
    s.append('<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + f'" fill="none" stroke="{color}" stroke-width="2.2"/>')
    for i, (x, y) in enumerate(pts):
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>')
        v = series[key][periods[i]]
        above = key.startswith('Data disclosed') or i == 0
        dy = -10 if above else 21
        dx = -18 if i == 3 else 0
        text(s, x + dx, y + dy, f'{v:.0f}%', 14, anchor='middle', fill=color)
text(s, 12, 308, "Longpre et al., Economies of Open Intelligence (2025), Table 1. The last period is the study's 2025 period.", 14)
s += ['</g></svg>']
(A / 'disclosure-trend.svg').write_text('\n'.join(s) + '\n')
print('Built four figures in', A)
