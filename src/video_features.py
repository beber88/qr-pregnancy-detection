"""
Video Feature Extraction — Temporal Urine Behavior Analysis

A photograph captures ONE moment. A video captures BEHAVIOR:
- How light interacts with the liquid over time
- How particles settle or stay suspended
- How the surface moves and reflects
- How color shifts as the camera/liquid stabilize
- Micro-movements invisible in a single frame

We DON'T know what the pregnancy signature looks like in video.
That's the point. We extract rich temporal features and let the
model discover which patterns correlate with pregnancy.

Feature groups:
  T1. Color dynamics (how RGB/HSV change over time)
  T2. Turbidity dynamics (how cloudiness changes)
  T3. Optical flow (liquid movement patterns)
  T4. Texture dynamics (surface pattern evolution)
  T5. Spectral dynamics (Layla R-channel behavior over time)
  T6. Settling behavior (particle/sediment dynamics)
  T7. Statistical temporal signatures (autocorrelation, periodicity)

Total: ~45 temporal features per video

Research use only. Not a diagnostic test.
"""

import cv2
import numpy as np
import logging
from collections import defaultdict


def extract_video_features(video_path, sample_rate=3):
    """
    Extract temporal behavior features from a urine video.

    Args:
        video_path: Path to video file
        sample_rate: Frames to sample per second (default 3)

    Returns:
        dict with ~45 temporal features, or None if video unreadable.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.warning(f"Cannot open video: {video_path}")
        return None

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0

    if duration < 2 or total_frames < 30:
        logging.warning(f"Video too short: {duration:.1f}s")
        return None

    frame_interval = max(1, int(fps / sample_rate))

    # Collect per-frame measurements
    timeseries = defaultdict(list)
    prev_gray = None
    frame_count = 0

    for i in range(0, total_frames, frame_interval):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]

        # ROI: center region where liquid is
        y1, y2 = int(h * 0.25), int(h * 0.75)
        x1, x2 = int(w * 0.25), int(w * 0.75)
        roi = frame[y1:y2, x1:x2]

        # --- Per-frame color ---
        r = float(np.mean(roi[:, :, 2]))
        g = float(np.mean(roi[:, :, 1]))
        b = float(np.mean(roi[:, :, 0]))
        total_rgb = r + g + b
        if total_rgb < 1:
            total_rgb = 1

        timeseries["r"].append(r)
        timeseries["g"].append(g)
        timeseries["b"].append(b)
        timeseries["r_ratio"].append(r / total_rgb)
        timeseries["rg_ratio"].append(r / max(g, 1))
        timeseries["rb_ratio"].append(r / max(b, 1))

        # HSV
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        timeseries["hue"].append(float(np.mean(hsv_roi[:, :, 0])))
        timeseries["saturation"].append(float(np.mean(hsv_roi[:, :, 1])))
        timeseries["value"].append(float(np.mean(hsv_roi[:, :, 2])))

        # --- Per-frame turbidity ---
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        lap = cv2.Laplacian(gray, cv2.CV_64F)
        timeseries["turbidity"].append(float(np.var(lap)))

        # Edge density (relates to transparency/clarity)
        edges = cv2.Canny(gray, 50, 150)
        timeseries["edge_density"].append(float(np.mean(edges > 0)))

        # --- Optical flow (liquid movement) ---
        if prev_gray is not None and prev_gray.shape == gray.shape:
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, gray, None,
                pyr_scale=0.5, levels=3, winsize=15,
                iterations=3, poly_n=5, poly_sigma=1.2, flags=0
            )
            mag = np.sqrt(flow[:, :, 0]**2 + flow[:, :, 1]**2)
            ang = np.arctan2(flow[:, :, 1], flow[:, :, 0])

            timeseries["flow_magnitude"].append(float(np.mean(mag)))
            timeseries["flow_max"].append(float(np.max(mag)))
            timeseries["flow_std"].append(float(np.std(mag)))
            # Directional coherence: are particles moving in same direction?
            timeseries["flow_coherence"].append(float(np.abs(np.mean(np.exp(1j * ang)))))

        # --- Texture (LBP-like) ---
        # Use local variance as texture measure (faster than full LBP per frame)
        local_var = cv2.blur(gray.astype(float)**2, (7, 7)) - cv2.blur(gray.astype(float), (7, 7))**2
        timeseries["texture_var"].append(float(np.mean(local_var)))

        # --- Frame difference (change between consecutive frames) ---
        if prev_gray is not None and prev_gray.shape == gray.shape:
            diff = cv2.absdiff(gray, prev_gray)
            timeseries["frame_diff"].append(float(np.mean(diff)))

        prev_gray = gray.copy()
        frame_count += 1

    cap.release()

    if frame_count < 5:
        logging.warning(f"Too few frames extracted: {frame_count}")
        return None

    # === Build features from timeseries ===
    features = {}

    # Metadata
    features["video_duration"] = round(duration, 2)
    features["video_frames_sampled"] = frame_count
    features["video_fps"] = round(fps, 1)

    # --- T1: Color dynamics ---
    for ch in ["r_ratio", "rg_ratio", "rb_ratio", "hue", "saturation", "value"]:
        series = np.array(timeseries[ch])
        features[f"t_{ch}_mean"] = round(float(np.mean(series)), 6)
        features[f"t_{ch}_std"] = round(float(np.std(series)), 6)
        # Trend: is it going up or down over the video?
        if len(series) > 2:
            slope = np.polyfit(range(len(series)), series, 1)[0]
            features[f"t_{ch}_trend"] = round(float(slope), 8)
        else:
            features[f"t_{ch}_trend"] = 0.0

    # --- T2: Turbidity dynamics ---
    turb = np.array(timeseries["turbidity"])
    features["t_turb_mean"] = round(float(np.mean(turb)), 4)
    features["t_turb_std"] = round(float(np.std(turb)), 4)
    features["t_turb_trend"] = round(float(np.polyfit(range(len(turb)), turb, 1)[0]), 6) if len(turb) > 2 else 0.0
    # Settling: does turbidity decrease over time? (particles settling)
    if len(turb) > 4:
        first_half = np.mean(turb[:len(turb)//2])
        second_half = np.mean(turb[len(turb)//2:])
        features["t_turb_settling"] = round(float(second_half - first_half), 4)
    else:
        features["t_turb_settling"] = 0.0

    # --- T3: Optical flow dynamics ---
    if timeseries["flow_magnitude"]:
        flow_mag = np.array(timeseries["flow_magnitude"])
        features["t_flow_mean"] = round(float(np.mean(flow_mag)), 4)
        features["t_flow_std"] = round(float(np.std(flow_mag)), 4)
        features["t_flow_trend"] = round(float(np.polyfit(range(len(flow_mag)), flow_mag, 1)[0]), 6) if len(flow_mag) > 2 else 0.0
        # Does movement slow down? (settling/calming)
        if len(flow_mag) > 4:
            features["t_flow_decay"] = round(float(np.mean(flow_mag[len(flow_mag)//2:]) / max(np.mean(flow_mag[:len(flow_mag)//2]), 0.001)), 4)
        else:
            features["t_flow_decay"] = 1.0

        # Flow coherence (are particles moving together?)
        if timeseries["flow_coherence"]:
            coherence = np.array(timeseries["flow_coherence"])
            features["t_flow_coherence_mean"] = round(float(np.mean(coherence)), 4)
        else:
            features["t_flow_coherence_mean"] = 0.0

        # Peak flow (maximum activity moment)
        features["t_flow_peak"] = round(float(np.max(flow_mag)), 4)
        features["t_flow_peak_time"] = round(float(np.argmax(flow_mag)) / len(flow_mag), 4)
    else:
        features["t_flow_mean"] = 0.0
        features["t_flow_std"] = 0.0
        features["t_flow_trend"] = 0.0
        features["t_flow_decay"] = 1.0
        features["t_flow_coherence_mean"] = 0.0
        features["t_flow_peak"] = 0.0
        features["t_flow_peak_time"] = 0.0

    # --- T4: Texture dynamics ---
    tex = np.array(timeseries["texture_var"])
    features["t_texture_mean"] = round(float(np.mean(tex)), 4)
    features["t_texture_std"] = round(float(np.std(tex)), 4)
    features["t_texture_trend"] = round(float(np.polyfit(range(len(tex)), tex, 1)[0]), 6) if len(tex) > 2 else 0.0

    # --- T5: Spectral dynamics (Layla R-channel over time) ---
    r_ratio = np.array(timeseries["r_ratio"])
    # How stable is the R-ratio? Pregnancy urine may have different optical stability
    features["t_layla_r_stability"] = round(float(np.std(r_ratio) / max(np.mean(r_ratio), 0.001)), 6)
    # Autocorrelation at lag=1: how predictable is the R-ratio sequence?
    if len(r_ratio) > 3:
        r_centered = r_ratio - np.mean(r_ratio)
        autocorr = np.correlate(r_centered, r_centered, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        if autocorr[0] > 0:
            features["t_layla_r_autocorr"] = round(float(autocorr[1] / autocorr[0]), 6)
        else:
            features["t_layla_r_autocorr"] = 0.0
    else:
        features["t_layla_r_autocorr"] = 0.0

    # --- T6: Settling behavior ---
    if timeseries["frame_diff"]:
        diffs = np.array(timeseries["frame_diff"])
        features["t_activity_mean"] = round(float(np.mean(diffs)), 4)
        features["t_activity_trend"] = round(float(np.polyfit(range(len(diffs)), diffs, 1)[0]), 6) if len(diffs) > 2 else 0.0
        # Time to calm: how many seconds until activity drops below mean?
        activity_threshold = np.mean(diffs) * 0.5
        calm_idx = np.where(diffs < activity_threshold)[0]
        if len(calm_idx) > 0:
            features["t_time_to_calm"] = round(float(calm_idx[0]) / sample_rate, 2)
        else:
            features["t_time_to_calm"] = round(duration, 2)
    else:
        features["t_activity_mean"] = 0.0
        features["t_activity_trend"] = 0.0
        features["t_time_to_calm"] = 0.0

    # --- T7: Statistical temporal signatures ---
    # Overall "dynamism" score: how much does the video change?
    all_changes = []
    for key in ["r_ratio", "turbidity", "saturation"]:
        s = np.array(timeseries[key])
        if len(s) > 1:
            cv = np.std(s) / max(np.mean(s), 0.001)
            all_changes.append(cv)
    features["t_overall_dynamism"] = round(float(np.mean(all_changes)), 6) if all_changes else 0.0

    # Complexity: approximate entropy of the R-ratio signal
    features["t_r_ratio_complexity"] = round(_approx_entropy(r_ratio), 6)

    return features


def _approx_entropy(series, m=2, r_factor=0.2):
    """
    Simplified approximate entropy of a time series.
    Higher = more complex/unpredictable behavior.
    """
    if len(series) < 10:
        return 0.0

    r = r_factor * np.std(series)
    if r < 1e-10:
        return 0.0

    def _count_matches(template, data, r_val):
        count = 0
        for i in range(len(data) - len(template) + 1):
            if np.max(np.abs(template - data[i:i+len(template)])) < r_val:
                count += 1
        return count

    N = len(series)
    counts_m = []
    counts_m1 = []

    for i in range(N - m):
        template_m = series[i:i+m]
        template_m1 = series[i:i+m+1] if i + m + 1 <= N else None

        c_m = _count_matches(template_m, series, r) / (N - m + 1)
        counts_m.append(c_m)

        if template_m1 is not None and i + m + 1 <= N:
            c_m1 = _count_matches(template_m1, series, r) / (N - m)
            counts_m1.append(c_m1)

    phi_m = np.mean(np.log(np.array(counts_m) + 1e-10))
    phi_m1 = np.mean(np.log(np.array(counts_m1) + 1e-10)) if counts_m1 else phi_m

    return abs(phi_m - phi_m1)


def extract_raw_frame_sequence(video_path, sample_rate=3, target_size=(224, 224)):
    """
    Extract raw frame sequence for deep learning (CNN+LSTM/Transformer).

    Instead of hand-crafted features, this returns the actual pixel data
    as a tensor that can be fed directly into a neural network.

    The network learns WHAT TO LOOK FOR — we don't tell it.

    Args:
        video_path: Path to video file
        sample_rate: Frames per second to sample
        target_size: Frame resize target (for CNN input)

    Returns:
        dict with:
          'frames': numpy array of shape (N, H, W, 3) — RGB frames
          'timestamps': list of float timestamps in seconds
          'metadata': dict with video info
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = max(1, int(fps / sample_rate))

    frames = []
    timestamps = []

    for i in range(0, total_frames, frame_interval):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            break

        # Convert BGR→RGB for standard ML pipelines
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Resize to standard input size
        frame_resized = cv2.resize(frame_rgb, target_size)

        frames.append(frame_resized)
        timestamps.append(i / fps)

    cap.release()

    if not frames:
        return None

    return {
        "frames": np.array(frames, dtype=np.uint8),
        "timestamps": timestamps,
        "metadata": {
            "fps": fps,
            "total_frames": total_frames,
            "sampled_frames": len(frames),
            "duration": total_frames / fps,
            "source": video_path,
        }
    }
