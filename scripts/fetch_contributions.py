#!/usr/bin/env python3
"""Fetch a GitHub user's public contribution calendar (no token needed) and
write data/contributions.json with raw days + derived stats.

Usage: python fetch_contributions.py [username]
Writes: data/contributions.json
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

USERNAME = "nqn0x"  # <-- change to your GitHub username
OUTPUT = "data/contributions.json"


def fetch(username):
    url = f"https://github.com/users/{username}/contributions"
    resp = requests.get(url, headers={"User-Agent": "profile-readme-bot"})
    resp.raise_for_status()
    return resp.text


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    days = []
    for td in soup.select("td[data-date]"):
        date = td.get("data-date")
        level = td.get("data-level")
        days.append({
            "date": date,
            "level": int(level) if level is not None else 0,
        })
    if not days:
        # fallback selector for markup variants that use <rect> cells
        for rect in soup.select("rect.ContributionCalendar-day"):
            date = rect.get("data-date")
            level = rect.get("data-level")
            days.append({
                "date": date,
                "level": int(level) if level is not None else 0,
            })
    return days


def derive_stats(days):
    days_sorted = sorted([d for d in days if d["date"]], key=lambda d: d["date"])
    total = sum(1 for d in days_sorted if d["level"] > 0)

    longest = running = 0
    for d in days_sorted:
        if d["level"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0

    current = 0
    for d in reversed(days_sorted):
        if d["level"] > 0:
            current += 1
        else:
            break

    best_day = max(days_sorted, key=lambda d: d["level"], default=None)

    monthly = {}
    for d in days_sorted:
        month = d["date"][:7]
        monthly[month] = monthly.get(month, 0) + (1 if d["level"] > 0 else 0)

    return {
        "total_active_days": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best_day,
        "monthly_active_days": monthly,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else USERNAME
    html = fetch(username)
    days = parse(html)
    if not days:
        print("Warning: no contribution cells parsed -- GitHub markup may have changed.")
    stats = derive_stats(days)

    Path("data").mkdir(exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump({"username": username, "days": days, "stats": stats}, f, indent=2)
    print(f"Wrote {OUTPUT}: {len(days)} days, {stats['total_active_days']} active")


if __name__ == "__main__":
    main()
