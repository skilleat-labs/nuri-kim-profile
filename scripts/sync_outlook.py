#!/usr/bin/env python3
"""Sync calendar.html BUSY_DATES to Microsoft Outlook via Graph API."""

import json
import os
import re
import hashlib
import requests
from datetime import datetime, timedelta

TENANT_ID     = os.environ["AZURE_TENANT_ID"]
CLIENT_ID     = os.environ["AZURE_CLIENT_ID"]
CLIENT_SECRET = os.environ["AZURE_CLIENT_SECRET"]
USER_EMAIL    = os.environ["AZURE_USER_EMAIL"]

TRACKING_FILE = ".github/outlook_sync_ids.json"
CALENDAR_FILE = "calendar.html"
GRAPH_BASE    = "https://graph.microsoft.com/v1.0"


# ── AUTH ────────────────────────────────────────────────────────────────────

def get_access_token() -> str:
    url  = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope":         "https://graph.microsoft.com/.default",
        "grant_type":    "client_credentials",
    }
    r = requests.post(url, data=data, timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]


# ── PARSE ────────────────────────────────────────────────────────────────────

def parse_busy_dates(html: str) -> list[dict]:
    """Parse BUSY_DATES string array from calendar.html."""
    match = re.search(r"const BUSY_DATES\s*=\s*\[(.*?)\];", html, re.DOTALL)
    if not match:
        raise ValueError("BUSY_DATES not found in calendar.html")

    raw_entries = re.findall(r"'([^']+)'", match.group(1))
    events = []

    for entry in raw_entries:
        # Format: YYYY-MM-DD:레이블:status[:HH:MM[:HH:MM[:online|offline]]]
        parts  = entry.split(":")
        date   = parts[0]
        label  = parts[1] if len(parts) > 1 else ""
        status = parts[2] if len(parts) > 2 else "confirmed"

        # Skip blocked slots and empty-label entries
        if status == "blocked" or not label:
            continue

        start_time = f"{parts[3]}:{parts[4]}" if len(parts) >= 5 else ""
        end_time   = f"{parts[5]}:{parts[6]}" if len(parts) >= 7 else ""
        mode       = parts[7]                  if len(parts) >= 8 else ""

        events.append({
            "date":      date,
            "label":     label,
            "status":    status,
            "startTime": start_time,
            "endTime":   end_time,
            "mode":      mode,
        })

    return events


# ── HELPERS ──────────────────────────────────────────────────────────────────

def event_key(e: dict) -> str:
    return f"{e['date']}:{e['label']}"

def event_hash(e: dict) -> str:
    raw = "|".join([e["date"], e["label"], e["status"], e["startTime"], e["endTime"], e["mode"]])
    return hashlib.md5(raw.encode()).hexdigest()

def build_graph_event(e: dict) -> dict:
    date       = e["date"]
    label      = e["label"]
    start_time = e["startTime"]
    end_time   = e["endTime"]
    mode       = e["mode"]
    status     = e["status"]

    show_as = "oof" if status == "휴무" else ("tentative" if status == "tentative" else "busy")
    location = {"displayName": "온라인"} if mode == "online" else ({"displayName": "오프라인"} if mode == "offline" else None)

    if start_time and end_time:
        payload = {
            "subject": label,
            "start":   {"dateTime": f"{date}T{start_time}:00", "timeZone": "Asia/Seoul"},
            "end":     {"dateTime": f"{date}T{end_time}:00",   "timeZone": "Asia/Seoul"},
            "showAs":  show_as,
        }
    else:
        next_day = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        payload = {
            "subject":  label,
            "isAllDay": True,
            "start":    {"dateTime": f"{date}T00:00:00",     "timeZone": "Asia/Seoul"},
            "end":      {"dateTime": f"{next_day}T00:00:00", "timeZone": "Asia/Seoul"},
            "showAs":   show_as,
        }

    if location:
        payload["location"] = location

    return payload


# ── GRAPH API ────────────────────────────────────────────────────────────────

def headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def create_event(token: str, payload: dict) -> str:
    r = requests.post(f"{GRAPH_BASE}/users/{USER_EMAIL}/calendar/events",
                      headers=headers(token), json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["id"]

def update_event(token: str, oid: str, payload: dict) -> None:
    r = requests.patch(f"{GRAPH_BASE}/users/{USER_EMAIL}/calendar/events/{oid}",
                       headers=headers(token), json=payload, timeout=30)
    r.raise_for_status()

def delete_event(token: str, oid: str) -> None:
    r = requests.delete(f"{GRAPH_BASE}/users/{USER_EMAIL}/calendar/events/{oid}",
                        headers={"Authorization": f"Bearer {token}"}, timeout=30)
    if r.status_code not in (204, 404):
        r.raise_for_status()


# ── TRACKING ─────────────────────────────────────────────────────────────────

def load_tracking() -> dict:
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_tracking(data: dict) -> None:
    with open(TRACKING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    with open(CALENDAR_FILE, encoding="utf-8") as f:
        html = f.read()

    events = parse_busy_dates(html)
    print(f"Parsed {len(events)} events from calendar.html")

    token    = get_access_token()
    tracking = load_tracking()

    current  = {event_key(e): e for e in events}
    created = updated = deleted = 0

    # Create / update
    for key, event in current.items():
        h     = event_hash(event)
        graph = build_graph_event(event)

        if key not in tracking:
            oid = create_event(token, graph)
            tracking[key] = {"id": oid, "hash": h}
            print(f"  ✚ Created : {key}")
            created += 1
        elif tracking[key]["hash"] != h:
            update_event(token, tracking[key]["id"], graph)
            tracking[key]["hash"] = h
            print(f"  ↻ Updated : {key}")
            updated += 1

    # Delete removed events
    for key in list(tracking.keys()):
        if key not in current:
            delete_event(token, tracking[key]["id"])
            del tracking[key]
            print(f"  ✖ Deleted : {key}")
            deleted += 1

    save_tracking(tracking)
    print(f"\nDone — created {created}, updated {updated}, deleted {deleted}")


if __name__ == "__main__":
    main()
