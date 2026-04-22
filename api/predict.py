"""
Vercel Serverless Function — /api/predict
Accepts photo or video upload, returns real AI prediction.

Research use only. Experimental probability model. Not a diagnostic test.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import tempfile
import pickle
import traceback

import cv2
import numpy as np
from io import BytesIO

# Add project paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
DISCLAIMER = "Research use only. Experimental probability model. Not a diagnostic test."

# ── Load models at cold start ──
_models = {}
_loaded = False


def _load_models():
    global _models, _loaded
    if _loaded:
        return

    if not os.path.isdir(MODELS_DIR):
        return

    for fname in os.listdir(MODELS_DIR):
        if not fname.endswith(".pkl"):
            continue
        try:
            with open(os.path.join(MODELS_DIR, fname), "rb") as f:
                data = pickle.load(f)
            tier = data.get("tier", "unknown")
            _models[tier] = {
                "model": data["model"],
                "features": data["features"],
                "auc": data.get("best_auc", 0),
            }
        except Exception:
            pass

    _loaded = True


# ── Feature extraction (self-contained, no imports needed) ──

def extract_photo_features(image_bytes):
    """Extract 32 features from photo bytes."""
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return None

    img = cv2.resize(img, (512, 512))

    # Detect ROI
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 25, 5)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    h, w = gray.shape
    mask = np.zeros((h, w), dtype=np.uint8)

    if contours:
        largest = max(contours, key=cv2.contourArea)
        ratio = cv2.contourArea(largest) / (h * w)
        if 0.05 < ratio < 0.85:
            cv2.drawContours(mask, [largest], -1, 255, -1)
        else:
            mask[int(h*0.2):int(h*0.8), int(w*0.2):int(w*0.8)] = 255
    else:
        mask[int(h*0.2):int(h*0.8), int(w*0.2):int(w*0.8)] = 255

    n_px = max(cv2.countNonZero(mask), 1)
    roi_bgr = cv2.bitwise_and(img, img, mask=mask)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    roi_hsv = cv2.bitwise_and(hsv, hsv, mask=mask)
    roi_gray = cv2.bitwise_and(gray, gray, mask=mask)

    b_mean = np.sum(roi_bgr[:,:,0]) / n_px
    g_mean = np.sum(roi_bgr[:,:,1]) / n_px
    r_mean = np.sum(roi_bgr[:,:,2]) / n_px
    brightness = np.sum(roi_hsv[:,:,2]) / n_px

    lap = cv2.Laplacian(roi_gray, cv2.CV_64F)
    lap_vals = lap[mask > 0]
    turbidity = float(np.var(lap_vals)) if len(lap_vals) > 0 else 0.0

    hue_vals = roi_hsv[:,:,0][mask > 0]
    if len(hue_vals) > 0:
        hist, _ = np.histogram(hue_vals, bins=18, range=(0, 180))
        dominant_hue = float(np.argmax(hist) * 10)
        hue_spread = float(np.std(hue_vals))
    else:
        dominant_hue, hue_spread = 0.0, 0.0

    edges = cv2.Canny(roi_gray, 50, 150)
    edge_intensity = float(np.sum(edges[mask > 0] > 0) / n_px)

    blurred_g = cv2.GaussianBlur(roi_gray, (9, 9), 2)
    circles = cv2.HoughCircles(blurred_g, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
                                param1=50, param2=30, minRadius=3, maxRadius=30)
    bubble_count = 0 if circles is None else len(circles[0])

    gray_vals = gray[mask > 0]
    contrast = float(np.std(gray_vals)) if len(gray_vals) > 0 else 0.0
    sat_vals = roi_hsv[:,:,1][mask > 0]
    saturation = float(np.mean(sat_vals)) if len(sat_vals) > 0 else 0.0
    rgb_vals = roi_bgr[mask > 0]
    color_variance = float(np.var(rgb_vals)) if len(rgb_vals) > 0 else 0.0
    yellowness = (r_mean + g_mean) / (2 * max(b_mean, 1))
    gy_ratio = g_mean / max(r_mean, 1)

    # Layla features
    roi_pixels = img[mask > 0].astype(float)
    if len(roi_pixels) > 0:
        r_v, g_v, b_v = roi_pixels[:,2], roi_pixels[:,1], roi_pixels[:,0]
        total = r_v + g_v + b_v
        total = np.where(total < 1, 1, total)
        r_ratio = r_v / total
        layla_r_ratio = float(np.mean(r_ratio))
        layla_rg_ratio = float(np.mean(r_v / np.where(g_v < 1, 1, g_v)))
        layla_rb_ratio = float(np.mean(r_v / np.where(b_v < 1, 1, b_v)))
        layla_r_ratio_std = float(np.std(r_ratio))
        r_mean_v = np.mean(r_v)
        r_std_v = max(np.std(r_v), 0.001)
        layla_r_skew = float(np.mean(((r_v - r_mean_v) / r_std_v) ** 3))
        layla_r_dominant = float(np.mean((r_v > g_v) & (r_v > b_v)))
    else:
        layla_r_ratio = layla_rg_ratio = layla_rb_ratio = 0.0
        layla_r_ratio_std = layla_r_skew = layla_r_dominant = 0.0

    # LAB
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    lab_px = lab[mask > 0].astype(float)
    if len(lab_px) > 0:
        lab_L = float(np.mean(lab_px[:,0]))
        lab_a = float(np.mean(lab_px[:,1])) - 128
        lab_b_val = float(np.mean(lab_px[:,2])) - 128
        lab_chroma = float(np.sqrt(lab_a**2 + lab_b_val**2))
    else:
        lab_L = lab_a = lab_b_val = lab_chroma = 0.0

    # Concentration
    hsv_px = hsv[mask > 0].astype(float)
    if len(hsv_px) > 0:
        s_v, v_v = hsv_px[:,1], hsv_px[:,2]
        conc_sv = float(np.mean(s_v * (255 - v_v)))
        h_v = hsv_px[:,0]
        ym = (h_v >= 15) & (h_v <= 35)
        conc_yellow_sat = float(np.mean(s_v[ym])) if np.any(ym) else 0.0
        conc_darkness = 255.0 - float(np.mean(v_v))
    else:
        conc_sv = conc_yellow_sat = conc_darkness = 0.0

    # Texture - simplified (no skimage dependency)
    texture_score = float(np.var(gray[mask > 0])) if len(gray[mask > 0]) > 0 else 0.0

    return {
        "r_mean": round(r_mean, 4), "g_mean": round(g_mean, 4), "b_mean": round(b_mean, 4),
        "brightness": round(brightness, 4), "turbidity": round(turbidity, 4),
        "dominant_hue": round(dominant_hue, 4), "hue_spread": round(hue_spread, 4),
        "texture_score": round(texture_score, 4), "edge_intensity": round(edge_intensity, 6),
        "bubble_count": int(bubble_count), "contrast": round(contrast, 4),
        "saturation": round(saturation, 4), "color_variance": round(color_variance, 4),
        "yellowness": round(yellowness, 4), "gy_ratio": round(gy_ratio, 4),
        "cal_card_found": 0, "cal_delta_e": -1.0, "cal_quality_ok": 0, "cal_cct_estimate": 5500,
        "layla_r_ratio": round(layla_r_ratio, 6), "layla_rg_ratio": round(layla_rg_ratio, 6),
        "layla_rb_ratio": round(layla_rb_ratio, 6), "layla_r_ratio_std": round(layla_r_ratio_std, 6),
        "layla_r_skew": round(layla_r_skew, 6), "layla_r_dominant": round(layla_r_dominant, 6),
        "lab_L": round(lab_L, 4), "lab_a": round(lab_a, 4), "lab_b": round(lab_b_val, 4),
        "lab_chroma": round(lab_chroma, 4),
        "conc_proxy_sv": round(conc_sv, 4), "conc_proxy_yellow_sat": round(conc_yellow_sat, 4),
        "conc_darkness": round(conc_darkness, 4),
    }


def extract_video_features(video_bytes):
    """Extract 42 temporal features from video bytes."""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(video_bytes)
        tmp_path = tmp.name

    try:
        cap = cv2.VideoCapture(tmp_path)
        if not cap.isOpened():
            return None

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        if duration < 2:
            cap.release()
            return None

        sample_rate = 3
        frame_interval = max(1, int(fps / sample_rate))

        from collections import defaultdict
        ts = defaultdict(list)
        prev_gray = None

        for i in range(0, total_frames, frame_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret:
                break

            h, w = frame.shape[:2]
            roi = frame[int(h*0.25):int(h*0.75), int(w*0.25):int(w*0.75)]
            r = float(np.mean(roi[:,:,2]))
            g = float(np.mean(roi[:,:,1]))
            b = float(np.mean(roi[:,:,0]))
            total_rgb = max(r+g+b, 1)

            ts["r_ratio"].append(r/total_rgb)
            ts["rg_ratio"].append(r/max(g,1))
            ts["rb_ratio"].append(r/max(b,1))

            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            ts["hue"].append(float(np.mean(hsv_roi[:,:,0])))
            ts["saturation"].append(float(np.mean(hsv_roi[:,:,1])))
            ts["value"].append(float(np.mean(hsv_roi[:,:,2])))

            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            lap = cv2.Laplacian(gray, cv2.CV_64F)
            ts["turbidity"].append(float(np.var(lap)))
            ts["edge_density"].append(float(np.mean(cv2.Canny(gray, 50, 150) > 0)))

            if prev_gray is not None and prev_gray.shape == gray.shape:
                flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                mag = np.sqrt(flow[:,:,0]**2 + flow[:,:,1]**2)
                ts["flow_magnitude"].append(float(np.mean(mag)))
                ts["flow_max"].append(float(np.max(mag)))
                ts["flow_std"].append(float(np.std(mag)))
                ts["flow_coherence"].append(float(np.abs(np.mean(np.exp(1j * np.arctan2(flow[:,:,1], flow[:,:,0]))))))
                ts["frame_diff"].append(float(np.mean(cv2.absdiff(gray, prev_gray))))

            local_var = cv2.blur(gray.astype(float)**2, (7,7)) - cv2.blur(gray.astype(float), (7,7))**2
            ts["texture_var"].append(float(np.mean(local_var)))
            prev_gray = gray.copy()

        cap.release()

        feats = {"video_duration": round(duration, 2), "video_frames_sampled": len(ts["r_ratio"]), "video_fps": round(fps, 1)}

        for ch in ["r_ratio","rg_ratio","rb_ratio","hue","saturation","value"]:
            s = np.array(ts[ch])
            feats[f"t_{ch}_mean"] = round(float(np.mean(s)), 6)
            feats[f"t_{ch}_std"] = round(float(np.std(s)), 6)
            feats[f"t_{ch}_trend"] = round(float(np.polyfit(range(len(s)), s, 1)[0]), 8) if len(s) > 2 else 0.0

        turb = np.array(ts["turbidity"])
        feats["t_turb_mean"] = round(float(np.mean(turb)), 4)
        feats["t_turb_std"] = round(float(np.std(turb)), 4)
        feats["t_turb_trend"] = round(float(np.polyfit(range(len(turb)), turb, 1)[0]), 6) if len(turb) > 2 else 0.0
        feats["t_turb_settling"] = round(float(np.mean(turb[len(turb)//2:]) - np.mean(turb[:len(turb)//2])), 4) if len(turb) > 4 else 0.0

        if ts["flow_magnitude"]:
            fm = np.array(ts["flow_magnitude"])
            feats["t_flow_mean"] = round(float(np.mean(fm)), 4)
            feats["t_flow_std"] = round(float(np.std(fm)), 4)
            feats["t_flow_trend"] = round(float(np.polyfit(range(len(fm)), fm, 1)[0]), 6) if len(fm) > 2 else 0.0
            feats["t_flow_decay"] = round(float(np.mean(fm[len(fm)//2:]) / max(np.mean(fm[:len(fm)//2]), 0.001)), 4) if len(fm) > 4 else 1.0
            feats["t_flow_coherence_mean"] = round(float(np.mean(ts["flow_coherence"])), 4)
            feats["t_flow_peak"] = round(float(np.max(fm)), 4)
            feats["t_flow_peak_time"] = round(float(np.argmax(fm)) / len(fm), 4)
        else:
            for k in ["t_flow_mean","t_flow_std","t_flow_trend","t_flow_coherence_mean","t_flow_peak","t_flow_peak_time"]:
                feats[k] = 0.0
            feats["t_flow_decay"] = 1.0

        tex = np.array(ts["texture_var"])
        feats["t_texture_mean"] = round(float(np.mean(tex)), 4)
        feats["t_texture_std"] = round(float(np.std(tex)), 4)
        feats["t_texture_trend"] = round(float(np.polyfit(range(len(tex)), tex, 1)[0]), 6) if len(tex) > 2 else 0.0

        rr = np.array(ts["r_ratio"])
        feats["t_layla_r_stability"] = round(float(np.std(rr) / max(np.mean(rr), 0.001)), 6)
        if len(rr) > 3:
            rc = rr - np.mean(rr)
            ac = np.correlate(rc, rc, mode='full')
            ac = ac[len(ac)//2:]
            feats["t_layla_r_autocorr"] = round(float(ac[1]/ac[0]), 6) if ac[0] > 0 else 0.0
        else:
            feats["t_layla_r_autocorr"] = 0.0

        if ts["frame_diff"]:
            diffs = np.array(ts["frame_diff"])
            feats["t_activity_mean"] = round(float(np.mean(diffs)), 4)
            feats["t_activity_trend"] = round(float(np.polyfit(range(len(diffs)), diffs, 1)[0]), 6) if len(diffs) > 2 else 0.0
            thr = np.mean(diffs) * 0.5
            ci = np.where(diffs < thr)[0]
            feats["t_time_to_calm"] = round(float(ci[0]) / sample_rate, 2) if len(ci) > 0 else round(duration, 2)
        else:
            feats["t_activity_mean"] = feats["t_activity_trend"] = feats["t_time_to_calm"] = 0.0

        changes = []
        for key in ["r_ratio","turbidity","saturation"]:
            s = np.array(ts[key])
            if len(s) > 1:
                changes.append(np.std(s) / max(np.mean(s), 0.001))
        feats["t_overall_dynamism"] = round(float(np.mean(changes)), 6) if changes else 0.0
        feats["t_r_ratio_complexity"] = 0.0  # Simplified for serverless

        return feats
    finally:
        os.unlink(tmp_path)


def predict_with_model(features, input_type):
    """Run prediction using best available model."""
    _load_models()
    if not _models:
        return None, "No models available"

    # Select best model for input type
    if input_type == "video":
        for tier in ["Video", "Combined"]:
            if tier in _models:
                m = _models[tier]
                import pandas as pd
                avail = {k: features.get(k, 0) for k in m["features"]}
                X = pd.DataFrame([avail])[m["features"]]
                proba = m["model"].predict_proba(X)[0][1]
                return float(proba), tier
    else:
        for tier in ["Photo_V2", "Combined"]:
            if tier in _models:
                m = _models[tier]
                import pandas as pd
                avail = {k: features.get(k, 0) for k in m["features"]}
                X = pd.DataFrame([avail])[m["features"]]
                proba = m["model"].predict_proba(X)[0][1]
                return float(proba), tier

    return None, "No compatible model"


def parse_multipart(body, content_type):
    """Parse multipart form data to extract file."""
    boundary = content_type.split("boundary=")[-1].encode()
    parts = body.split(b"--" + boundary)

    for part in parts:
        if b"filename=" not in part:
            continue
        # Extract filename
        header_end = part.find(b"\r\n\r\n")
        if header_end == -1:
            continue
        headers = part[:header_end].decode(errors="ignore")
        file_data = part[header_end + 4:]
        if file_data.endswith(b"\r\n"):
            file_data = file_data[:-2]

        # Get filename
        fname = ""
        for line in headers.split("\n"):
            if "filename=" in line:
                fname = line.split('filename="')[1].split('"')[0] if 'filename="' in line else ""
                break

        return file_data, fname

    return None, None


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            content_type = self.headers.get("Content-Type", "")
            body = self.rfile.read(content_length)

            file_data, filename = parse_multipart(body, content_type)
            if file_data is None:
                self._respond(400, {"error": "No file found in request"})
                return

            ext = os.path.splitext(filename)[1].lower()
            is_video = ext in (".mp4", ".mov", ".avi")

            if is_video:
                features = extract_video_features(file_data)
                input_type = "video"
            else:
                features = extract_photo_features(file_data)
                input_type = "photo"

            if features is None:
                self._respond(422, {"error": "Could not process file", "input_type": input_type, "disclaimer": DISCLAIMER})
                return

            proba, tier = predict_with_model(features, input_type)

            self._respond(200, {
                "probability": round(proba, 4) if proba is not None else None,
                "input_type": input_type,
                "model_tier": tier,
                "status": "success" if proba is not None else "model_not_available",
                "disclaimer": DISCLAIMER,
            })

        except Exception as e:
            self._respond(500, {"error": str(e), "trace": traceback.format_exc()[:500], "disclaimer": DISCLAIMER})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def _respond(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
