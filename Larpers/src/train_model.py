import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Map extensions to numeric categories for ML Processing
# e.g.: 0 = logs/junk, 1 = system/code, 2 = media/documents
EXTENSION_MAP = {
    ".log": 0, ".tmp": 0, ".iso": 0,
    ".py": 1, ".js": 1, ".txt": 1, ".idx": 1,
    ".mp4": 2, ".docx": 2, ".png": 2, ".unknown": 1
}

def generate_synthetic_data(num_samples=10000):
    """
    Generates thousands of simulated filesystem rows to deeply train the AI model.
    Feature Output Mapping: [days_since_access, size_mb, extension_category, path_depth, is_temp_dir, has_backup_keyword]
    Label Output Mapping: 0 = Redundant/Trash, 1 = Important, 2 = Uncertain/Hold
    """
    print(f"Synthesizing {num_samples} Advanced Enterprise data variations...")
    X_train = []
    y_train = []
    
    for _ in range(num_samples):
        # Generate Random Properties
        ext = np.random.choice(list(EXTENSION_MAP.keys()))
        ext_cat = EXTENSION_MAP[ext]
        size_mb = np.random.uniform(0.1, 1000.0) # Anywhere from 100KB to 1GB
        days_old = np.random.uniform(0, 1000)    # Age from 0 days to 1000 days
        path_depth = np.random.randint(1, 15)   # Depth from 1 to 15
        is_temp_dir = np.random.choice([0, 1], p=[0.8, 0.2])
        has_backup_keyword = np.random.choice([0, 1], p=[0.9, 0.1])
        
        # Determine the Ground Truth "Label" based on complex real-world logic
        
        # Rule 1: High probability of Redundant if in temp dir or has backup keyword and is somewhat old
        if (is_temp_dir == 1 or has_backup_keyword == 1) and days_old > 30:
            label = 0
        # Rule 2: Large files in deep paths that are old are Redundant
        elif path_depth > 8 and days_old > 365:
            label = 0
        # Rule 3: JUNK extensions that are old are Redundant
        elif ext_cat == 0 and days_old > 90:
            label = 0
        # Rule 4: System/Code files that are new are Important
        elif ext_cat == 1 and days_old < 60:
            label = 1
        # Rule 5: Media/Docs that are not extremely old are Important
        elif ext_cat == 2 and days_old < 730:
            label = 1
        # Rule 6: Extremely old junk is always Redundant
        elif days_old > 700 and ext_cat == 0:
            label = 0
        else:
            label = 2 # Catch-all: Uncertain state, hold for user review.
            
        X_train.append([days_old, size_mb, ext_cat, path_depth, is_temp_dir, has_backup_keyword])
        y_train.append(label)
        
    return np.array(X_train), np.array(y_train)

def train_and_save_model(model_dir="models"):
    """
    Trains a robust Random Forest model on the synthetic data and Serializes it structurally.
    """
    # Ensure we are in the right directory relative to the project root
    # If this is run from src/, we need to go up one level to find models/
    current_dir = os.path.basename(os.getcwd())
    if current_dir == "src":
        model_dir = os.path.join("..", "models")
    
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    print("Generating Advanced Dataset...")
    X, y = generate_synthetic_data(10000)
    
    print("Training Machine Learning Model Engine: Random Forest Classifier (v4)")
    clf = RandomForestClassifier(n_estimators=150, max_depth=15, random_state=42)
    clf.fit(X, y)
    
    accuracy = clf.score(X, y)
    print(f"Model Training complete. Engine Baseline Accuracy: {accuracy * 100:.2f}%")
    
    # Save the Neural/Mathematical Weights structurally to the Hard Drive
    model_path = os.path.join(model_dir, "asos_classifier_v4.pkl")
    joblib.dump(clf, model_path)
    print(f"✅ Securely Exported true AI Model payload to -> {model_path}")

if __name__ == "__main__":
    train_and_save_model()
