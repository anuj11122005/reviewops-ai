import argparse
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import mlflow
import mlflow.sklearn

os.environ["MLFLOW_TRACKING_URI"] = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv("MLFLOW_S3_ENDPOINT_URL", "http://minio:9000")
os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID", "admin")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY", "password")
def train(data_path: str):
    """Train the model and log to MLflow."""
    print(f"Loading data from {data_path}...")
    
    # Load dataset
    df = pd.read_csv(data_path)
    X = df[["complexity", "size", "function_count", "comment_ratio"]]
    y = df["is_bug"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Set experiment
    mlflow.set_experiment("bug_prediction")
    
    with mlflow.start_run() as run:
        print("Training model...")
        model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        model.fit(X_train, y_train)
        
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds, zero_division=0)
        rec = recall_score(y_test, preds, zero_division=0)
        
        print(f"Metrics: Accuracy={acc:.3f}, Precision={prec:.3f}, Recall={rec:.3f}")
        
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("precision", prec)
        mlflow.log_metric("recall", rec)
        
        # Log model
        mlflow.sklearn.log_model(model, "model", registered_model_name="BugPredictor")
        
        if acc < 0.6:
            mlflow.set_tag("promoted", "false")
            print("Model underperformed. Marked as not-promoted.")
        else:
            mlflow.set_tag("promoted", "true")
            print("Model registered and promoted.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, default="data/synthetic_bugs.csv", help="Path to training data")
    args = parser.parse_args()
    
    train(args.data)
