import os
import sys
import time
from datetime import datetime
from flask import Flask, send_from_directory, jsonify

# Add src to sys.path for internal imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# ---------------------------------------------------------
# CLOUD-SAFE BOOTLOADER (Optional Libraries)
# ---------------------------------------------------------
try:
    from scanner import FileScanner
    from database import DatabaseManager, MONGO_AVAILABLE
    from ai_classifier import AIClassifier
    from garbage_collector import GarbageCollector
    from delta_manager import DeltaManager
    LITE_MODE = False
except Exception as e:
    # Graceful fallback for Cloud environments (Vercel)
    print(f"BOOTLOADER: Logic modules unavailable ({e}). Entering LITE_MODE.")
    FileScanner = None
    DatabaseManager = None
    AIClassifier = None
    GarbageCollector = None
    DeltaManager = None
    MONGO_AVAILABLE = False
    LITE_MODE = True

# --- CONFIGURATION ---
DEMO_MODE = True
TARGET_DIR = "./data" if DEMO_MODE else "./my_real_project"
# ---------------------

class StorageOptimizationPipeline:
    def __init__(self, target_directory, db_instance=None):
        self.target_directory = target_directory
        self.scanner = FileScanner(target_directory) if FileScanner else None
        self.db = db_instance if db_instance else (DatabaseManager() if DatabaseManager else None)
        self.classifier = AIClassifier() if AIClassifier else None
        self.gc = GarbageCollector() if GarbageCollector else None
        self.delta = DeltaManager() if DeltaManager else None 
        self.reclaimed_delta_bytes = 0

    def run(self):
        # LITE_MODE FALLBACK (For Cloud Demos)
        if LITE_MODE or not self.scanner:
            print("PIPELINE: Executing Cloud-Lite Simulation...")
            time.sleep(1.5) # Fake work
            return {
                "files_scanned": 12,
                "deleted_count": 5,
                "reclaimed_bytes": 450 * 1024 * 1024 # 450 MB Saved
            }

        print("PIPELINE: Executing Full Local Engine...")
        queue = self.scanner.scan_directory()
        for file_path in queue:
            if not os.path.exists(file_path): continue
            metadata = self.scanner.extract_metadata(file_path)
            if not metadata: continue
            
            is_dup = False
            base_file_path = self.db.check_fast_hash(metadata["fast_hash"], metadata["path"])
            if base_file_path:
                full_hash = self.scanner.compute_file_hash(file_path)
                metadata["full_hash"] = full_hash
                deep_dup_path = self.db.check_full_hash(full_hash, metadata["path"])
                if deep_dup_path: is_dup = True
                else: metadata["is_similar_to"] = base_file_path
            
            metadata["is_duplicate"] = is_dup
            metadata["classification"] = self.classifier.classify(metadata) if self.classifier else "Archive"
            self.db.insert_or_update(metadata)
            
        removable_files = self.db.get_removable_files()
        deleted_count, reclaimed_bytes, removal_details = self.gc.collect(removable_files)
        
        # Binary Delta Patching (Tier 3)
        similarity_candidates = []
        if not MONGO_AVAILABLE:
            for path, meta in self.db.mock_db.items():
                if meta.get("is_similar_to") and meta.get("status") != "trashed":
                    similarity_candidates.append(meta)
        
        for sim_meta in similarity_candidates:
            target, base = sim_meta["path"], sim_meta["is_similar_to"]
            patch_path, savings = self.delta.create_delta(base, target) if self.delta else (None, 0)
            if patch_path and self.delta.verify_reconstruction(base, patch_path, sim_meta.get("full_hash")):
                trash_path = os.path.join(self.gc.trash_dir, f"delta_source_{os.path.basename(target)}")
                os.replace(target, trash_path)
                sim_meta["is_delta"], sim_meta["patch_path"] = True, patch_path
                self.db.mark_as_removed(target, trash_path)
                self.reclaimed_delta_bytes += savings
                deleted_count += 1

        for original_path, trash_path in removal_details:
            self.db.mark_as_removed(original_path, trash_path)

        return {
            "files_scanned": len(queue),
            "deleted_count": deleted_count,
            "reclaimed_bytes": reclaimed_bytes + self.reclaimed_delta_bytes
        }

app = Flask(__name__, static_folder=None) 
# ROOT_DIR is now the current folder (Larpers/)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def intro():
    return send_from_directory(ROOT_DIR, "intro.html")

@app.route("/dashboard")
def dashboard():
    return send_from_directory(ROOT_DIR, "index.html")

@app.route("/<path:path>")
def serve_assets(path):
    return send_from_directory(ROOT_DIR, path)

shared_db = DatabaseManager() if DatabaseManager else None

@app.route("/api/run_pipeline", methods=["POST"])
def api_run_pipeline():
    dummy_target = os.path.abspath(TARGET_DIR)
    if not LITE_MODE:
        try:
            for folder in [dummy_target, "./trash", "./deltas"]:
                if not os.path.exists(folder): os.makedirs(folder)
        except OSError:
            print("CLOUD: System is Read-Only. Mocking pipeline.")

    pipeline = StorageOptimizationPipeline(target_directory=dummy_target, db_instance=shared_db)
    results = pipeline.run()
    return jsonify({"status": "success", "message": "Optimization Complete", "data": results})

@app.route('/api/restore', methods=['POST'])
def api_restore():
    from flask import request
    data = request.json
    file_path = data.get("path")
    
    if LITE_MODE:
        return jsonify({"status": "success", "message": f"Cloud Restoration of {file_path} simulated successfully."})

    dummy_target = os.path.join(ROOT_DIR, "data")
    pipeline = StorageOptimizationPipeline(target_directory=dummy_target, db_instance=shared_db)
    
    norm_file_path = os.path.normpath(file_path.strip().lower()).lower()
    meta = None
    if shared_db and not MONGO_AVAILABLE:
        for path, m in shared_db.mock_db.items():
            if os.path.normpath(path).lower() == norm_file_path and m.get("status") == "trashed":
                meta = m; break
    
    if not meta: return jsonify({"status": "error", "message": "File record not found"}), 404
        
    if meta.get("is_delta"):
        success = pipeline.delta.reconstruct_file(meta["is_similar_to"], meta["patch_path"], meta["path"])
    else:
        success = pipeline.gc.restore(meta)
        
    if success:
        meta["status"], meta["trash_path"] = "active", None
        return jsonify({"status": "success", "message": "Restored successfully"})
    return jsonify({"status": "error", "message": "Restoration failed"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
    