#!/usr/bin/env python3
"""
Survey Image Sorter for Urin Test Group
========================================
This script sorts WhatsApp-downloaded survey images into the correct
POSITIVE/NEGATIVE folders based on download timestamps.

INSTRUCTIONS:
1. Open WhatsApp Web -> Urin test group
2. For each survey set (April 29-May 1), click on images and download them
   using the three-dots menu -> Download (הורדה)
3. Download ALL images for ONE survey set, then run this script
4. The script will find new files in Downloads and move them to the correct folder
5. Repeat for the next survey set

Usage:
  python3 sort_surveys.py                    # Interactive mode
  python3 sort_surveys.py --auto             # Auto-detect new files and prompt for folder
  python3 sort_surveys.py --list             # Show the complete mapping
"""

import os
import sys
import shutil
import time
from pathlib import Path
from datetime import datetime

DOWNLOADS = Path.home() / "Downloads"
BASE = Path.home() / "QR PROJECT" / "PICTURES - VIDEO"
POSITIVE = BASE / "POSITIVE"
NEGATIVE = BASE / "NEGATIVE"

# Complete survey mapping: (date, set_number, type) -> folder_number
MAPPING = {
    # APRIL 29 - POSITIVE (Pregnant)
    ("Apr29", 1, "P"): 42,
    ("Apr29", 6, "P"): 43,
    ("Apr29", 7, "P"): 44,
    ("Apr29", 8, "P"): 45,
    ("Apr29", 15, "P"): 46,
    ("Apr29", 19, "P"): 47,
    # APRIL 29 - NEGATIVE (Non-Pregnant)
    ("Apr29", 2, "N"): 31,
    ("Apr29", 3, "N"): 32,
    ("Apr29", 4, "N"): 33,
    ("Apr29", 5, "N"): 34,
    ("Apr29", 9, "N"): 35,
    ("Apr29", 10, "N"): 36,
    ("Apr29", 11, "N"): 37,
    ("Apr29", 12, "N"): 38,
    ("Apr29", 13, "N"): 39,
    ("Apr29", 14, "N"): 40,
    ("Apr29", 16, "N"): 41,
    ("Apr29", 17, "N"): 42,
    ("Apr29", 18, "N"): 43,
    ("Apr29", 20, "N"): 44,
    ("Apr29", 21, "N"): 45,
    # APRIL 30 - POSITIVE (Pregnant)
    ("Apr30", 4, "P"): 48,
    ("Apr30", 7, "P"): 49,
    ("Apr30", 10, "P"): 50,
    ("Apr30", 11, "P"): 51,
    # APRIL 30 - NEGATIVE (Non-Pregnant)
    ("Apr30", 1, "N"): 46,
    ("Apr30", 2, "N"): 47,
    ("Apr30", 3, "N"): 48,
    ("Apr30", 5, "N"): 49,
    ("Apr30", 6, "N"): 50,
    ("Apr30", 8, "N"): 51,
    ("Apr30", 9, "N"): 52,
    # MAY 1 - POSITIVE (Pregnant)
    ("May1", 3, "P"): 52,
    # MAY 1 - NEGATIVE (Non-Pregnant)
    ("May1", 1, "N"): 53,
    ("May1", 2, "N"): 54,
    ("May1", 4, "N"): 55,
    ("May1", 5, "N"): 56,
    ("May1", 6, "N"): 57,
    ("May1", 7, "N"): 58,
    ("May1", 8, "N"): 59,
    ("May1", 9, "N"): 60,
}

# Readable mapping for display
READABLE = []
for (date, num, ptype), folder in sorted(MAPPING.items(), key=lambda x: (x[0][0], x[1])):
    category = "POSITIVE" if ptype == "P" else "NEGATIVE"
    label = "Pregnant" if ptype == "P" else "Non-Pregnant"
    READABLE.append((date, num, label, category, folder))


def show_mapping():
    """Display the complete survey-to-folder mapping."""
    print("\n" + "=" * 70)
    print("COMPLETE SURVEY MAPPING")
    print("=" * 70)

    current_date = ""
    for date, num, label, category, folder in READABLE:
        if date != current_date:
            current_date = date
            print(f"\n--- {date} ---")
        print(f"  #{num:2d} {label:20s} -> {category}/{folder}")

    print(f"\nTotal: {len(READABLE)} survey sets")
    print(f"  POSITIVE folders: 42-52 (11 sets)")
    print(f"  NEGATIVE folders: 31-60 (30 sets)")


def find_new_files(since_seconds=300):
    """Find files in Downloads modified within the last N seconds."""
    now = time.time()
    new_files = []
    for f in DOWNLOADS.iterdir():
        if f.is_file() and f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp'):
            if now - f.stat().st_mtime < since_seconds:
                new_files.append(f)
    return sorted(new_files, key=lambda f: f.stat().st_mtime)


def move_files_to_folder(files, category, folder_num):
    """Move files to the specified POSITIVE/NEGATIVE folder."""
    if category.upper() == "POSITIVE" or category.upper() == "P":
        dest = POSITIVE / str(folder_num)
    else:
        dest = NEGATIVE / str(folder_num)

    dest.mkdir(parents=True, exist_ok=True)

    moved = []
    for f in files:
        target = dest / f.name
        # Avoid overwriting
        if target.exists():
            base = f.stem
            ext = f.suffix
            i = 1
            while target.exists():
                target = dest / f"{base}_{i}{ext}"
                i += 1
        shutil.move(str(f), str(target))
        moved.append((f.name, target))
        print(f"  Moved: {f.name} -> {dest.name}/{target.name}")

    return moved


def interactive_mode():
    """Interactive step-by-step mode."""
    print("\n" + "=" * 70)
    print("SURVEY IMAGE SORTER - Interactive Mode")
    print("=" * 70)
    print("\nWorkflow:")
    print("1. In WhatsApp Web, download ALL images for one survey set")
    print("2. Come back here and press Enter")
    print("3. Tell me which survey set you just downloaded")
    print("4. I will move the files to the correct folder")
    print("5. Repeat for the next set")
    print("\nType 'list' to see the mapping, 'quit' to exit\n")

    while True:
        cmd = input("\nPress Enter after downloading a set (or type command): ").strip().lower()

        if cmd == 'quit' or cmd == 'q':
            print("Done!")
            break
        elif cmd == 'list':
            show_mapping()
            continue

        # Find new files
        new_files = find_new_files(since_seconds=120)

        if not new_files:
            print("No new image files found in Downloads (last 2 minutes).")
            print("Try downloading the images first, then press Enter.")
            continue

        print(f"\nFound {len(new_files)} new image(s):")
        for f in new_files:
            mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%H:%M:%S")
            print(f"  [{mtime}] {f.name}")

        # Ask which survey set
        print("\nWhich survey set is this?")
        date = input("  Date (Apr29/Apr30/May1): ").strip()
        num = input("  Set number (e.g. 1, 6, 15): ").strip()
        ptype = input("  Type - P(regnant) or N(on-Pregnant): ").strip().upper()

        if not date or not num or not ptype:
            print("Skipped. Files not moved.")
            continue

        try:
            num = int(num)
        except ValueError:
            print("Invalid number. Skipped.")
            continue

        key = (date, num, ptype[0])
        if key in MAPPING:
            folder_num = MAPPING[key]
            category = "POSITIVE" if ptype[0] == "P" else "NEGATIVE"
            print(f"\n-> Moving to {category}/{folder_num}")
            confirm = input("   Confirm? (y/n): ").strip().lower()
            if confirm == 'y':
                move_files_to_folder(new_files, category, folder_num)
                print("Done!")
            else:
                print("Skipped.")
        else:
            print(f"Survey set not found in mapping: {key}")
            print("Use 'list' to see all available sets.")


def auto_mode():
    """Auto-detect and prompt mode."""
    print("\nAuto mode: Looking for new files in Downloads...")
    new_files = find_new_files(since_seconds=300)

    if not new_files:
        print("No new image files found in Downloads (last 5 minutes).")
        return

    print(f"\nFound {len(new_files)} new image(s):")
    for f in new_files:
        mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%H:%M:%S")
        size_kb = f.stat().st_size // 1024
        print(f"  [{mtime}] {f.name} ({size_kb} KB)")

    print("\nEnter the target folder:")
    category = input("  Category (P/N): ").strip().upper()
    folder = input("  Folder number: ").strip()

    try:
        folder = int(folder)
    except ValueError:
        print("Invalid folder number.")
        return

    cat_name = "POSITIVE" if category == "P" else "NEGATIVE"
    print(f"\nMoving {len(new_files)} files to {cat_name}/{folder}")
    confirm = input("Confirm? (y/n): ").strip().lower()
    if confirm == 'y':
        move_files_to_folder(new_files, cat_name, folder)
        print("Done!")


if __name__ == "__main__":
    if "--list" in sys.argv:
        show_mapping()
    elif "--auto" in sys.argv:
        auto_mode()
    else:
        interactive_mode()
