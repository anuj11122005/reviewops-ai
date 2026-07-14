import os
import pandas as pd
import numpy as np

def generate_data(path: str, n_samples: int = 1000, drifted: bool = False):
    """Generate synthetic PR feature data for training/drift detection."""
    np.random.seed(42 if not drifted else 1337)
    
    # Base features
    complexity = np.random.gamma(shape=2.0, scale=5.0, size=n_samples)
    size = np.random.gamma(shape=500.0, scale=10.0, size=n_samples)
    function_count = np.random.poisson(lam=5.0, size=n_samples)
    comment_ratio = np.random.beta(a=2.0, b=5.0, size=n_samples)
    
    if drifted:
        # Introduce drift in size and complexity
        complexity = np.random.gamma(shape=4.0, scale=8.0, size=n_samples)
        size = np.random.gamma(shape=1000.0, scale=15.0, size=n_samples)
    
    # Calculate probability of a bug
    # Higher complexity, larger size, more functions -> higher chance of bug
    # Higher comment ratio -> lower chance of bug
    logit = (
        0.05 * complexity + 
        0.0005 * size + 
        0.1 * function_count - 
        2.0 * comment_ratio - 
        3.0
    )
    
    probs = 1 / (1 + np.exp(-logit))
    is_bug = np.random.binomial(1, probs)
    
    df = pd.DataFrame({
        "complexity": complexity,
        "size": size,
        "function_count": function_count,
        "comment_ratio": comment_ratio,
        "is_bug": is_bug
    })
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Generated {n_samples} samples at {path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, default="data/synthetic_bugs.csv")
    parser.add_argument("--drifted", action="store_true")
    parser.add_argument("--n_samples", type=int, default=1000)
    args = parser.parse_args()
    
    generate_data(args.path, args.n_samples, args.drifted)
