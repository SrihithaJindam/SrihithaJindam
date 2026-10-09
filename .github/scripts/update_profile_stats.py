import os
import re
import math
import urllib.request

def fetch_url(url, output_path, timeout=15):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read()
            if len(content) > 500: # ensure valid payload
                with open(output_path, "wb") as f:
                    f.write(content)
                print(f"Successfully updated {output_path}")
                return True
    except Exception as e:
        print(f"Warning: could not fetch {url}: {e}")
    return False

def update_spider_radar(commits=119, prs=32, issues=2, contribs=17, reviews=6, output_path="assets/spider-activity-chart.svg"):
    width = 700
    height = 220
    cx = 485
    cy = 114
    radius = 68

    categories = [
        {"name": "Commits", "label": f"Commits ({commits})", "count": commits, "val_ratio": 0.90, "angle_deg": -90},
        {"name": "PRs", "label": f"PRs ({prs})", "count": prs, "val_ratio": 0.72, "angle_deg": -18},
        {"name": "Contributed", "label": f"Contributed ({contribs})", "count": contribs, "val_ratio": 0.62, "angle_deg": 54},
        {"name": "Reviews", "label": f"Reviews ({reviews})", "count": reviews, "val_ratio": 0.42, "angle_deg": 126},
        {"name": "Issues", "label": f"Issues ({issues})", "count": issues, "val_ratio": 0.32, "angle_deg": 198},
    ]

    # Concentric pentagons
    rings = []
    for level in [0.25, 0.5, 0.75, 1.0]:
        r = radius * level
        pts = []
        for cat in categories:
            rad = math.radians(cat["angle_deg"])
            x = cx + r * math.cos(rad)
            y = cy + r * math.sin(rad)
            pts.append(f"{x:.1f},{y:.1f}")
        stroke = "#30363d" if level == 1.0 else "#22272e"
        dash = "" if level == 1.0 else 'stroke-dasharray="2.5,2.5"'
        rings.append(f'<polygon points="{" ".join(pts)}" fill="none" stroke="{stroke}" stroke-width="1" {dash} />')

    # Spokes and labels
    spokes = []
    labels = []
    for cat in categories:
        rad = math.radians(cat["angle_deg"])
        x2 = cx + radius * math.cos(rad)
        y2 = cy + radius * math.sin(rad)
        spokes.append(f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#282f38" stroke-width="1.2" />')

        lx = cx + (radius + 16) * math.cos(rad)
        ly = cy + (radius + 14) * math.sin(rad)
        anchor = "middle"
        if math.cos(rad) > 0.2:
            anchor = "start"
            lx += 2
        elif math.cos(rad) < -0.2:
            anchor = "end"
            lx -= 2

        if cat["angle_deg"] == -90:
            ly += 2

        labels.append(f'''
        <text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" fill="#ffb74d" font-family="'Segoe UI', Ubuntu, 'Helvetica Neue', Sans-Serif" font-size="11px" font-weight="600">
            {cat['label']}
        </text>
        ''')

    # Data polygon (clean outline with very subtle transparent tint)
    data_pts = []
    nodes = []
    for cat in categories:
        rad = math.radians(cat["angle_deg"])
        r = radius * cat["val_ratio"]
        px = cx + r * math.cos(rad)
        py = cy + r * math.sin(rad)
        data_pts.append(f"{px:.1f},{py:.1f}")
        nodes.append(f'''
        <circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="#ff9800" stroke="#ffffff" stroke-width="1.2" />
        ''')

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <defs>
        <linearGradient id="spiderOutline" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#ffeb3b" />
            <stop offset="50%" stop-color="#ff9800" />
            <stop offset="100%" stop-color="#f44336" />
        </linearGradient>
    </defs>
    <style>
        * {{
            font-family: 'Segoe UI', Ubuntu, "Helvetica Neue", Sans-Serif;
        }}
    </style>

    <!-- Card Background -->
    <rect x="1" y="1" rx="6" ry="6" width="99.7%" height="99%" fill="#151515" stroke="#262c36" stroke-width="1" />

    <!-- Left Header -->
    <text x="35" y="38" font-size="20px" font-weight="700" fill="#ffffff">Activity Radar</text>
    <text x="35" y="56" font-size="11px" fill="#8b949e">Cross-repository contribution distribution</text>

    <!-- Stats Breakdown on Left -->
    <g transform="translate(35, 70)">
        <!-- Commits -->
        <g transform="translate(0, 10)">
            <circle cx="5" cy="5" r="4" fill="#ff9800" />
            <text x="18" y="9" fill="#9f9f9f" font-size="13px">Total Commits:</text>
            <text x="155" y="9" fill="#ffffff" font-size="13px" font-weight="600">{commits}</text>
        </g>
        <!-- PRs -->
        <g transform="translate(0, 34)">
            <circle cx="5" cy="5" r="4" fill="#ffb74d" />
            <text x="18" y="9" fill="#9f9f9f" font-size="13px">Pull Requests:</text>
            <text x="155" y="9" fill="#ffffff" font-size="13px" font-weight="600">{prs}</text>
        </g>
        <!-- Issues -->
        <g transform="translate(0, 58)">
            <circle cx="5" cy="5" r="4" fill="#f44336" />
            <text x="18" y="9" fill="#9f9f9f" font-size="13px">Issues Opened:</text>
            <text x="155" y="9" fill="#ffffff" font-size="13px" font-weight="600">{issues}</text>
        </g>
        <!-- Contributed Repos -->
        <g transform="translate(0, 82)">
            <circle cx="5" cy="5" r="4" fill="#ffeb3b" />
            <text x="18" y="9" fill="#9f9f9f" font-size="13px">Contributed Repos:</text>
            <text x="155" y="9" fill="#ffffff" font-size="13px" font-weight="600">{contribs}</text>
        </g>
        <!-- Code Reviews -->
        <g transform="translate(0, 106)">
            <circle cx="5" cy="5" r="4" fill="#ff7043" />
            <text x="18" y="9" fill="#9f9f9f" font-size="13px">Code Reviews:</text>
            <text x="155" y="9" fill="#ffffff" font-size="13px" font-weight="600">{reviews}</text>
        </g>
    </g>

    <!-- Subtle Center Divider -->
    <line x1="255" y1="25" x2="255" y2="195" stroke="#22272e" stroke-width="1" stroke-dasharray="3,3" />

    <!-- Radar Spider Grid on Right -->
    <g>
        {"".join(rings)}
        {"".join(spokes)}
    </g>

    <!-- Color Outlined Graph (Soft transparent tint + crisp outline) -->
    <polygon points="{" ".join(data_pts)}" fill="rgba(255, 152, 0, 0.06)" stroke="url(#spiderOutline)" stroke-width="2.2" stroke-linejoin="round" />
    {"".join(nodes)}

    <!-- Labels around Radar -->
    <g>
        {"".join(labels)}
    </g>

    <!-- Radar Sub-caption -->
    <text x="{cx}" y="206" text-anchor="middle" fill="#8b949e" font-size="10px">multi-dimensional contribution footprint</text>
</svg>
'''
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Successfully generated {output_path}")

def main():
    os.makedirs("assets", exist_ok=True)

    # 1. Update Streak Stats SVG
    streak_url = "https://streak-stats.demolab.com?user=SrihithaJindam&theme=dark&ring=FF9800&fire=F44336&currStreakNum=FF9800&currStreakLabel=FFB74D&sideNums=FFB74D&sideLabels=FFCC80&dates=B0BEC5&hide_border=true&border_radius=10&date_format=M%20j%5B%2C%20Y%5D&timezone=Europe%2FBerlin&starting_year=2022"
    fetch_url(streak_url, "assets/streak-stats.svg")

    # 2. Update Profile Details (Total Contributions Curve) SVG
    profile_details_url = "https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username=SrihithaJindam&theme=dark&name=Srihitha%20Jindam"
    fetch_url(profile_details_url, "assets/profile-details.svg")

    # 3. Fetch latest metrics and update Spider Activity Radar SVG
    stats_url = "https://github-profile-summary-cards.vercel.app/api/cards/stats?username=SrihithaJindam&theme=dark"
    commits, prs, issues, contribs = 119, 32, 2, 17
    try:
        req = urllib.request.Request(stats_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8")
            matches = re.findall(r'<text x="130"[^>]*>(\d+)</text>', html)
            if len(matches) >= 5:
                commits = int(matches[1])
                prs = int(matches[2])
                issues = int(matches[3])
                contribs = int(matches[4])
                print(f"Extracted live metrics: Commits={commits}, PRs={prs}, Issues={issues}, Contribs={contribs}")
    except Exception as e:
        print(f"Could not parse live stats ({e}), using default/cached metrics")

    update_spider_radar(commits=commits, prs=prs, issues=issues, contribs=contribs)

if __name__ == "__main__":
    main()
