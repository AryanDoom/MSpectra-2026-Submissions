import os
import time

try:
    import joblib
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("scikit-learn not installed. AI classifier will use backup rules.")

# Import the map so AI knows exactly what integers extensions translate to
try:
    from train_model import EXTENSION_MAP
except ImportError:
    EXTENSION_MAP = {".log": 0, ".tmp": 0, ".iso": 0, ".py": 1, ".js": 1, ".txt": 1, ".idx": 1, ".mp4": 2, ".docx": 2, ".png": 2, ".unknown": 1}

class AIClassifier:
    """
    True Machine Learning Inference Engine (v4).
    Loads real Serialized .pkl weights to identify File status based on 6 features.
    """
    def __init__(self, model_name="asos_classifier_v4.pkl"):
        # Search relative to the script's directory
        self.model = self._load_model(model_name)

    def _load_model(self, model_name):
        """
        Dynamically loads the compiled Intelligence Engine file from the hard drive.
        """
        if SKLEARN_AVAILABLE:
            abs_path = os.path.join(os.path.dirname(__file__), "..", "models", model_name)
            if os.path.exists(abs_path):
                print(f"Success: Loaded Serialized AI Engine v4 from {abs_path}")
                return joblib.load(abs_path)
            else:
                print(f"CRITICAL WARNING: Trained Payload {abs_path} not found.")
        return None

    def classify(self, metadata):
        """
        Returns a string classification label based on the file metadata using 6 dimensions.
        """
        current_time = time.time()
        
        last_access = metadata.get('last_access', current_time)
        days_since_access = (current_time - last_access) / (24 * 3600)
        size_mb = metadata.get('size', 0) / (1024 * 1024)
        
        # Extension mapping
        ext = metadata.get('extension', '.unknown')
        ext_cat = EXTENSION_MAP.get(ext, 1)

        # New Semantic Features
        path_depth = metadata.get('path_depth', 1)
        is_temp_dir = metadata.get('is_temp_dir', 0)
        has_backup_keyword = metadata.get('has_backup_keyword', 0)

        if self.model and SKLEARN_AVAILABLE:
            # Pushing extracted 6 features straight through the complex Neural Matrix
            features = np.array([[days_since_access, size_mb, ext_cat, path_depth, is_temp_dir, has_backup_keyword]])
            prediction = self.model.predict(features)[0]
            
            labels = {0: "Redundant", 1: "Important", 2: "Uncertain"}
            return labels.get(prediction, "Uncertain")
        else:
            # Absolute fallback Heuristic logic (enhanced)
            if is_temp_dir or has_backup_keyword:
                return "Redundant"
            if days_since_access > 365:   # older than ~1 year
                return "Redundant"
            elif days_since_access < 30:  # accessed in last 30 days
                return "Important"
            return "Uncertain"
