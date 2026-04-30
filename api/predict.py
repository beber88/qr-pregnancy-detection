"""
Vercel Serverless Function — /api/predict
Accepts photo or video upload, returns real AI prediction.

Supports RandomForest (JSON tree export) and LogisticRegression (JSON weights).
No sklearn dependency — pure numpy prediction.

Research use only. Experimental probability model. Not a diagnostic test.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import tempfile
import math
import traceback

import cv2
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
DISCLAIMER = "Research use only. Experimental probability model. Not a diagnostic test."

# ── Load JSON models at cold start ──
_models = {}
_loaded = False
_load_errors = []


def _load_models():
    global _models, _loaded, _load_errors
    if _loaded:
        return
    if not os.path.isdir(MODELS_DIR):
        _load_errors.append(f"No models dir: {MODELS_DIR}")
        _loaded = True
        return

    for fname in os.listdir(MODELS_DIR):
        if not fname.endswith(".json"):
            continue
        try:
            with open(os.path.join(MODELS_DIR, fname)) as f:
                data = json.load(f)
            tier = data.get("tier", "unknown")
            model_type = data.get("type", "unknown")
            # Prefer random_forest over logistic for same tier
            if tier not in _models or model_type == "random_forest":
                _models[tier] = data
        except Exception as e:
            _load_errors.append(f"{fname}: {e}")

    _loaded = True


def predict_logistic(model_data, features):
    """Run LogisticRegression prediction from JSON weights."""
    feature_names = model_data["features"]
    coef = np.array(model_data["coef"][0])
    intercept = model_data["intercept"][0]
    scaler = model_data.get("scaler")

    # Build feature vector — use scaler mean as default for missing features
    # This prevents zero-filling from causing extreme scaled values
    if scaler:
        mean = np.array(scaler["mean"])
        scale = np.array(scaler["scale"])
        scale = np.where(np.abs(scale) < 1e-10, 1.0, scale)
        X = np.array([features.get(f, mean[i]) for i, f in enumerate(feature_names)], dtype=float)
        X = (X - mean) / scale
    else:
        X = np.array([features.get(f, 0.0) for f in feature_names], dtype=float)

    z = float(np.dot(X, coef) + intercept)
    # Clamp to prevent overflow
    z = max(-20, min(20, z))
    prob = 1.0 / (1.0 + math.exp(-z))
    return prob


def predict_random_forest(model_data, features):
    """Run RandomForest prediction from JSON tree export. No sklearn needed."""
    feature_names = model_data["features"]
    scaler = model_data.get("scaler")

    # Build and scale feature vector
    if scaler:
        mean = np.array(scaler["mean"])
        scale = np.array(scaler["scale"])
        scale = np.where(np.abs(scale) < 1e-10, 1.0, scale)
        X = np.array([features.get(f, mean[i]) for i, f in enumerate(feature_names)], dtype=float)
        X = (X - mean) / scale
    else:
        X = np.array([features.get(f, 0.0) for f in feature_names], dtype=float)

    # Predict with each tree and average
    votes = []
    for tree_data in model_data["trees"]:
        feat = tree_data["feature"]
        thresh = tree_data["threshold"]
        left = tree_data["children_left"]
        right = tree_data["children_right"]
        value = tree_data["value"]

        # Traverse tree
        node = 0
        while feat[node] >= 0:  # -2 means leaf
            if X[feat[node]] <= thresh[node]:
                node = left[node]
            else:
                node = right[node]

        # value[node] is [[count_class0, count_class1]]
        counts = value[node][0]
        total = sum(counts)
        prob_positive = counts[1] / total if total > 0 else 0.5
        votes.append(prob_positive)

    return float(np.mean(votes))


def predict_model(model_data, features):
    """Predict using the appropriate model type."""
    model_type = model_data.get("type", "logistic")
    if model_type == "random_forest":
        return predict_random_forest(model_data, features)
    return predict_logistic(model_data, features)


# ── Feature extraction (self-contained) ──

def extract_photo_features(image_bytes):
    """Extract 32 features from photo bytes."""
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return None

    img = cv2.resize(img, (512, 512))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    # ROI detection
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 25, 5)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros((h, w), dtype=np.uint8)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        if 0.05 < cv2.contourArea(largest) / (h * w) < 0.85:
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
        hist_h, _ = np.histogram(hue_vals, bins=18, range=(0, 180))
        dominant_hue = float(np.argmax(hist_h) * 10)
        hue_spread = float(np.std(hue_vals))
    else:
        dominant_hue = hue_spread = 0.0

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
    texture_score = float(np.var(gray[mask > 0])) if len(gray[mask > 0]) > 0 else 0.0

    # Layla
    roi_px = img[mask > 0].astype(float)
    if len(roi_px) > 0:
        rv, gv, bv = roi_px[:,2], roi_px[:,1], roi_px[:,0]
        t = np.where((rv+gv+bv) < 1, 1, rv+gv+bv)
        rr = rv / t
        layla_r_ratio = float(np.mean(rr))
        layla_rg_ratio = float(np.mean(rv / np.where(gv<1,1,gv)))
        layla_rb_ratio = float(np.mean(rv / np.where(bv<1,1,bv)))
        layla_r_ratio_std = float(np.std(rr))
        rm, rs = np.mean(rv), max(np.std(rv), 0.001)
        layla_r_skew = float(np.mean(((rv-rm)/rs)**3))
        layla_r_dominant = float(np.mean((rv>gv) & (rv>bv)))
    else:
        layla_r_ratio=layla_rg_ratio=layla_rb_ratio=layla_r_ratio_std=layla_r_skew=layla_r_dominant=0.0

    # LAB
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    lp = lab[mask > 0].astype(float)
    if len(lp) > 0:
        lab_L, lab_a, lab_b_val = float(np.mean(lp[:,0])), float(np.mean(lp[:,1]))-128, float(np.mean(lp[:,2]))-128
        lab_chroma = float(np.sqrt(lab_a**2 + lab_b_val**2))
    else:
        lab_L=lab_a=lab_b_val=lab_chroma=0.0

    # Concentration
    hp = hsv[mask > 0].astype(float)
    if len(hp) > 0:
        sv, vv = hp[:,1], hp[:,2]
        conc_sv = float(np.mean(sv*(255-vv)))
        hv = hp[:,0]; ym = (hv>=15)&(hv<=35)
        conc_yellow_sat = float(np.mean(sv[ym])) if np.any(ym) else 0.0
        conc_darkness = 255.0 - float(np.mean(vv))
    else:
        conc_sv=conc_yellow_sat=conc_darkness=0.0

    return {
        "r_mean":round(r_mean,4),"g_mean":round(g_mean,4),"b_mean":round(b_mean,4),
        "brightness":round(brightness,4),"turbidity":round(turbidity,4),
        "dominant_hue":round(dominant_hue,4),"hue_spread":round(hue_spread,4),
        "texture_score":round(texture_score,4),"edge_intensity":round(edge_intensity,6),
        "bubble_count":int(bubble_count),"contrast":round(contrast,4),
        "saturation":round(saturation,4),"color_variance":round(color_variance,4),
        "yellowness":round(yellowness,4),"gy_ratio":round(gy_ratio,4),
        "cal_card_found":0,"cal_delta_e":-1.0,"cal_quality_ok":0,"cal_cct_estimate":5500,
        "layla_r_ratio":round(layla_r_ratio,6),"layla_rg_ratio":round(layla_rg_ratio,6),
        "layla_rb_ratio":round(layla_rb_ratio,6),"layla_r_ratio_std":round(layla_r_ratio_std,6),
        "layla_r_skew":round(layla_r_skew,6),"layla_r_dominant":round(layla_r_dominant,6),
        "lab_L":round(lab_L,4),"lab_a":round(lab_a,4),"lab_b":round(lab_b_val,4),
        "lab_chroma":round(lab_chroma,4),
        "conc_proxy_sv":round(conc_sv,4),"conc_proxy_yellow_sat":round(conc_yellow_sat,4),
        "conc_darkness":round(conc_darkness,4),
    }


def extract_video_features(video_bytes):
    """Extract temporal features from video bytes."""
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
            cap.release(); return None

        interval = max(1, int(fps / 3))
        from collections import defaultdict
        ts = defaultdict(list)
        prev_gray = None

        for i in range(0, total_frames, interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret: break
            fh, fw = frame.shape[:2]
            roi = frame[int(fh*0.25):int(fh*0.75), int(fw*0.25):int(fw*0.75)]
            r,g,b = float(np.mean(roi[:,:,2])), float(np.mean(roi[:,:,1])), float(np.mean(roi[:,:,0]))
            t = max(r+g+b, 1)
            ts["r_ratio"].append(r/t); ts["rg_ratio"].append(r/max(g,1)); ts["rb_ratio"].append(r/max(b,1))
            hsv_r = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            ts["hue"].append(float(np.mean(hsv_r[:,:,0])))
            ts["saturation"].append(float(np.mean(hsv_r[:,:,1])))
            ts["value"].append(float(np.mean(hsv_r[:,:,2])))
            gy = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            ts["turbidity"].append(float(np.var(cv2.Laplacian(gy, cv2.CV_64F))))
            if prev_gray is not None and prev_gray.shape == gy.shape:
                flow = cv2.calcOpticalFlowFarneback(prev_gray, gy, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                mag = np.sqrt(flow[:,:,0]**2 + flow[:,:,1]**2)
                ts["flow_magnitude"].append(float(np.mean(mag)))
                ts["flow_max"].append(float(np.max(mag)))
                ts["flow_std"].append(float(np.std(mag)))
                ts["flow_coherence"].append(float(np.abs(np.mean(np.exp(1j*np.arctan2(flow[:,:,1],flow[:,:,0]))))))
                ts["frame_diff"].append(float(np.mean(cv2.absdiff(gy, prev_gray))))
            lv = cv2.blur(gy.astype(float)**2,(7,7)) - cv2.blur(gy.astype(float),(7,7))**2
            ts["texture_var"].append(float(np.mean(lv)))
            prev_gray = gy.copy()
        cap.release()

        def trend(s): return float(np.polyfit(range(len(s)),s,1)[0]) if len(s)>2 else 0.0

        f = {"video_duration":round(duration,2),"video_frames_sampled":len(ts["r_ratio"]),"video_fps":round(fps,1)}
        for ch in ["r_ratio","rg_ratio","rb_ratio","hue","saturation","value"]:
            s = np.array(ts[ch])
            f[f"t_{ch}_mean"]=round(float(np.mean(s)),6); f[f"t_{ch}_std"]=round(float(np.std(s)),6); f[f"t_{ch}_trend"]=round(trend(s),8)
        turb = np.array(ts["turbidity"])
        f["t_turb_mean"]=round(float(np.mean(turb)),4); f["t_turb_std"]=round(float(np.std(turb)),4)
        f["t_turb_trend"]=round(trend(turb),6)
        f["t_turb_settling"]=round(float(np.mean(turb[len(turb)//2:])-np.mean(turb[:len(turb)//2])),4) if len(turb)>4 else 0.0
        if ts["flow_magnitude"]:
            fm=np.array(ts["flow_magnitude"])
            f["t_flow_mean"]=round(float(np.mean(fm)),4); f["t_flow_std"]=round(float(np.std(fm)),4)
            f["t_flow_trend"]=round(trend(fm),6)
            f["t_flow_decay"]=round(float(np.mean(fm[len(fm)//2:])/max(np.mean(fm[:len(fm)//2]),0.001)),4) if len(fm)>4 else 1.0
            f["t_flow_coherence_mean"]=round(float(np.mean(ts["flow_coherence"])),4)
            f["t_flow_peak"]=round(float(np.max(fm)),4)
            f["t_flow_peak_time"]=round(float(np.argmax(fm))/len(fm),4)
        else:
            for k in ["t_flow_mean","t_flow_std","t_flow_trend","t_flow_coherence_mean","t_flow_peak","t_flow_peak_time"]: f[k]=0.0
            f["t_flow_decay"]=1.0
        tex=np.array(ts["texture_var"])
        f["t_texture_mean"]=round(float(np.mean(tex)),4); f["t_texture_std"]=round(float(np.std(tex)),4); f["t_texture_trend"]=round(trend(tex),6)
        rr=np.array(ts["r_ratio"])
        f["t_layla_r_stability"]=round(float(np.std(rr)/max(np.mean(rr),0.001)),6)
        if len(rr)>3:
            rc=rr-np.mean(rr); ac=np.correlate(rc,rc,mode='full'); ac=ac[len(ac)//2:]
            f["t_layla_r_autocorr"]=round(float(ac[1]/ac[0]),6) if ac[0]>0 else 0.0
        else: f["t_layla_r_autocorr"]=0.0
        if ts["frame_diff"]:
            d=np.array(ts["frame_diff"]); f["t_activity_mean"]=round(float(np.mean(d)),4)
            f["t_activity_trend"]=round(trend(d),6)
            ci=np.where(d<np.mean(d)*0.5)[0]
            f["t_time_to_calm"]=round(float(ci[0])/3,2) if len(ci)>0 else round(duration,2)
        else: f["t_activity_mean"]=f["t_activity_trend"]=f["t_time_to_calm"]=0.0
        ch_list=[]
        for k in ["r_ratio","turbidity","saturation"]:
            s=np.array(ts[k])
            if len(s)>1: ch_list.append(np.std(s)/max(np.mean(s),0.001))
        f["t_overall_dynamism"]=round(float(np.mean(ch_list)),6) if ch_list else 0.0
        f["t_r_ratio_complexity"]=0.0
        return f
    finally:
        os.unlink(tmp_path)


def parse_multipart(body, content_type):
    """Parse multipart form data."""
    boundary = content_type.split("boundary=")[-1].encode()
    parts = body.split(b"--" + boundary)
    for part in parts:
        if b"filename=" not in part: continue
        header_end = part.find(b"\r\n\r\n")
        if header_end == -1: continue
        headers = part[:header_end].decode(errors="ignore")
        file_data = part[header_end + 4:]
        if file_data.endswith(b"\r\n"): file_data = file_data[:-2]
        fname = ""
        if 'filename="' in headers: fname = headers.split('filename="')[1].split('"')[0]
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
                self._respond(400, {"error": "No file in request"})
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

            _load_models()

            # Match input type to model tier
            if input_type == "video":
                search_order = ["Video", "Combined"]
            else:
                search_order = ["Photo_V2", "Combined"]

            prob = None
            tier_used = None
            model_type = None

            # Find best matching model
            for tier in search_order:
                if tier in _models:
                    prob = predict_model(_models[tier], features)
                    tier_used = tier
                    model_type = _models[tier].get("type", "unknown")
                    break

            # Fallback: try any available model
            if prob is None:
                for tier, m in _models.items():
                    prob = predict_model(m, features)
                    tier_used = tier
                    model_type = m.get("type", "unknown")
                    break

            # Include top features for debugging
            debug_feats = {}
            if features:
                for k in ["r_mean","g_mean","b_mean","layla_r_ratio","gy_ratio","brightness","dominant_hue"]:
                    if k in features:
                        debug_feats[k] = features[k]

            self._respond(200, {
                "probability": round(prob, 4) if prob is not None else None,
                "input_type": input_type,
                "model_tier": tier_used or "none",
                "model_type": model_type or "none",
                "status": "success" if prob is not None else "model_not_available",
                "features_sample": debug_feats,
                "disclaimer": DISCLAIMER,
            })

        except Exception as e:
            self._respond(500, {"error": str(e), "disclaimer": DISCLAIMER})

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
