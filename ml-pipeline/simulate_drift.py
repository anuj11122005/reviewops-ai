import os
import subprocess
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
import mlflow

def run_simulation():
    print("--- Drift Simulation and Retraining ---")
    
    # 1. Generate reference data and train initial model
    print("1. Generating reference data...")
    subprocess.run(["python", "generate_data.py", "--path", "data/reference.csv"], check=True)
    
    print("2. Training initial model on reference data...")
    subprocess.run(["python", "train.py", "--data", "data/reference.csv"], check=True)
    
    # 3. Generate drifted data
    print("3. Generating incoming data with drift...")
    subprocess.run(["python", "generate_data.py", "--path", "data/current.csv", "--drifted"], check=True)
    
    # 4. Detect drift using Evidently
    print("4. Running drift detection with Evidently...")
    ref_df = pd.read_csv("data/reference.csv")
    curr_df = pd.read_csv("data/current.csv")
    
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=ref_df, current_data=curr_df)
    report_dict = report.as_dict()
    
    dataset_drift = report_dict["metrics"][0]["result"]["dataset_drift"]
    print(f"Drift Detected: {dataset_drift}")
    
    # Save report
    os.makedirs("reports", exist_ok=True)
    report.save_html("reports/drift_report.html")
    print("Report saved to reports/drift_report.html")
    
    # 5. Retrain if drift detected
    if dataset_drift:
        print("5. Drift threshold exceeded! Triggering retraining...")
        # In a real system, we might combine old and new data, but here we just train on new data
        subprocess.run(["python", "train.py", "--data", "data/current.csv"], check=True)
        print("Retraining complete. New model logged to MLflow.")
    else:
        print("5. No significant drift detected. Skipping retraining.")

if __name__ == "__main__":
    run_simulation()
