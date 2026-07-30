#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M3U to SQLite Converter
by: serverblbas
"""

import sqlite3
import re
import urllib.request
import os

M3U_URL = "https://raw.githubusercontent.com/serverblbas-svg/iptveditor/refs/heads/main/serverblbas_m3u8.m3u"
DB_PATH = "channels.db"

def parse_m3u(content):
    """Parse M3U content and return list of channel dicts"""
    channels = []
    lines = content.splitlines()

    current = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("#EXTINF:"):
            # Parse EXTINF line
            current = {}

            # Extract tvg-name
            name_match = re.search(r'tvg-name="([^"]+)"', line)
            if name_match:
                current['tvg_name'] = name_match.group(1)

            # Extract tvg-id
            id_match = re.search(r'tvg-id="([^"]+)"', line)
            if id_match:
                current['tvg_id'] = id_match.group(1)

            # Extract tvg-logo
            logo_match = re.search(r'tvg-logo="([^"]+)"', line)
            if logo_match:
                current['tvg_logo'] = logo_match.group(1)

            # Extract tvg-group
            group_match = re.search(r'group-title="([^"]+)"', line)
            if group_match:
                current['group_title'] = group_match.group(1)

            # Extract channel name after last comma
            if ',' in line:
                current['name'] = line.rsplit(',', 1)[-1].strip()
            else:
                current['name'] = 'Unknown'

        elif line.startswith("http") and current:
            current['url'] = line
            channels.append(current)
            current = {}

    return channels

def create_database(channels):
    """Create SQLite database from channels list"""
    # Remove old DB if exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"🗑️  Removed old {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            tvg_name TEXT,
            tvg_id TEXT,
            tvg_logo TEXT,
            group_title TEXT,
            url TEXT
        )
    """)

    for ch in channels:
        cursor.execute("""
            INSERT INTO channels (name, tvg_name, tvg_id, tvg_logo, group_title, url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            ch.get('name', ''),
            ch.get('tvg_name', ''),
            ch.get('tvg_id', ''),
            ch.get('tvg_logo', ''),
            ch.get('group_title', ''),
            ch.get('url', '')
        ))

    conn.commit()
    conn.close()

def main():
    print("📥 Downloading M3U playlist...")
    try:
        req = urllib.request.Request(
            M3U_URL,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode('utf-8')
    except Exception as e:
        print(f"❌ Failed to download: {e}")
        print("💡 Tip: Download manually and save as 'playlist.m3u', then change M3U_URL to 'playlist.m3u'")
        return

    print(f"✅ Downloaded {len(content)} characters")

    print("🔍 Parsing channels...")
    channels = parse_m3u(content)
    print(f"✅ Found {len(channels)} channels")

    if not channels:
        print("⚠️  No channels found! Check M3U format.")
        return

    print("💾 Creating database...")
    create_database(channels)

    print(f"🎉 Success! Database saved as: {DB_PATH}")
    print(f"📊 Total channels: {len(channels)}")

    # Show first 5 channels
    print("\n📺 First 5 channels:")
    for i, ch in enumerate(channels[:5], 1):
        print(f"   {i}. {ch.get('name', 'Unknown')} | {ch.get('group_title', 'No Group')}")

if __name__ == "__main__":
    main()
