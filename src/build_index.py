"""
build_index.py — Scan PICTURES/, index all images and videos,
extract 1 frame per second from each video, and produce index.csv.

Output columns: filepath, subject_id, label, media_type, frame_number
"""

import os
import sys
import csv
import logging
from datetime import datetime

import cv2

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PICTURES_DIR = os.path.join(PROJECT_ROOT, "PICTURES")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
FRAMES_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "video_frames")
INDEX_CSV = os.path.join(PROCESSED_DIR, "index.csv")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")

IMAGE_EXT = {".jpg", ".jpeg", ".png"}
VIDEO_EXT = {".mp4", ".mov", ".avi"}


def setup_logging():
    os.makedirs(LOGS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOGS_DIR, f"build_index_{ts}.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return log_file


def extract_video_frames(video_path, subject_id, label_dir):
    """
    Extract 1 frame per second from a video file.
    Saves frames to data/raw/video_frames/<label_dir>/<subject_id>/
    Returns list of (frame_path, frame_number) tuples.
    """
    out_dir = os.path.join(FRAMES_DIR, label_dir, subject_id)
    os.makedirs(out_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.warning(f"Cannot open video: {video_path}")
        return []

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0  # fallback
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    logging.info(f"  Video: {os.path.basename(video_path)} — {fps:.1f}fps, {duration:.1f}s, {total_frames} frames")

    # Extract 1 frame per second
    frame_interval = int(round(fps))
    results = []
    frame_idx = 0
    sec = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_interval == 0:
            fname = f"frame_{sec:03d}.jpg"
            fpath = os.path.join(out_dir, fname)
            cv2.imwrite(fpath, frame)
            results.append((fpath, sec))
            sec += 1

        frame_idx += 1

    cap.release()
    logging.info(f"    Extracted {len(results)} frames")
    return results


def scan_group(group_name, label):
    """
    Scan PICTURES/<group_name>/ for subject folders.
    Returns list of index rows.
    """
    group_dir = os.path.join(PICTURES_DIR, group_name)
    rows = []

    if not os.path.isdir(group_dir):
        logging.warning(f"Directory not found: {group_dir}")
        return rows

    subject_dirs = sorted(
        [d for d in os.listdir(group_dir) if os.path.isdir(os.path.join(group_dir, d))],
        key=lambda x: int(x) if x.isdigit() else x,
    )

    logging.info(f"Scanning {group_name}: {len(subject_dirs)} subjects")

    for subject_id in subject_dirs:
        subject_path = os.path.join(group_dir, subject_id)
        files = sorted(os.listdir(subject_path))

        img_count = 0
        vid_count = 0

        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            fpath = os.path.join(subject_path, fname)

            if ext in IMAGE_EXT:
                rows.append({
                    "filepath": fpath,
                    "subject_id": f"{group_name}_{subject_id}",
                    "label": label,
                    "media_type": "photo",
                    "frame_number": 0,
                })
                img_count += 1

            elif ext in VIDEO_EXT:
                frames = extract_video_frames(fpath, subject_id, group_name)
                for frame_path, frame_num in frames:
                    rows.append({
                        "filepath": frame_path,
                        "subject_id": f"{group_name}_{subject_id}",
                        "label": label,
                        "media_type": "video_frame",
                        "frame_number": frame_num,
                    })
                vid_count += 1

        logging.info(f"  Subject {subject_id}: {img_count} photos, {vid_count} videos")

    return rows


def build_index():
    log_file = setup_logging()
    logging.info("=" * 60)
    logging.info("BUILD INDEX — Scanning PICTURES/")
    logging.info("=" * 60)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(FRAMES_DIR, exist_ok=True)

    all_rows = []

    # Scan POSITIVE (label=1)
    all_rows.extend(scan_group("POSITIVE", label=1))

    # Scan NEGATIVE (label=0) — will be empty for now
    all_rows.extend(scan_group("NEGATIVE", label=0))

    # Write index.csv
    fieldnames = ["filepath", "subject_id", "label", "media_type", "frame_number"]
    with open(INDEX_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    logging.info(f"\nIndex saved: {INDEX_CSV}")
    logging.info(f"Total rows: {len(all_rows)}")

    # Summary
    photos = sum(1 for r in all_rows if r["media_type"] == "photo")
    vframes = sum(1 for r in all_rows if r["media_type"] == "video_frame")
    subjects = len(set(r["subject_id"] for r in all_rows))
    logging.info(f"  Photos: {photos}")
    logging.info(f"  Video frames: {vframes}")
    logging.info(f"  Subjects: {subjects}")
    logging.info(f"Log: {log_file}")

    return INDEX_CSV


if __name__ == "__main__":
    build_index()
