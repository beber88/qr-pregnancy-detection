"""Vercel Serverless — /api/health"""
from http.server import BaseHTTPRequestHandler
import json
import os
import pickle

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        tiers = {}
        if os.path.isdir(MODELS_DIR):
            for f in os.listdir(MODELS_DIR):
                if f.endswith(".pkl"):
                    try:
                        with open(os.path.join(MODELS_DIR, f), "rb") as fh:
                            d = pickle.load(fh)
                        tiers[d.get("tier","?")] = {"auc": d.get("best_auc"), "classifier": d.get("classifier")}
                    except:
                        pass

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "healthy",
            "models_loaded": len(tiers),
            "tiers": tiers,
        }).encode())
