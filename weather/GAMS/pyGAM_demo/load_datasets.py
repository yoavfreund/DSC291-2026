"""
pyGAM Dataset Loader for Local Demo
This script loads the pyGAM datasets from the local datasets directory.
"""

import pandas as pd
import numpy as np
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(SCRIPT_DIR, 'datasets')

def _clean_X_y(X, y):
    """Clean and prepare X and y data."""
    if isinstance(X, pd.DataFrame):
        X = X.values
    if isinstance(y, pd.Series):
        y = y.values
    return X, y

def mcycle(return_X_y=True):
    """Motorcycle accident data."""
    df = pd.read_csv(os.path.join(DATASETS_DIR, 'mcycle.csv'))
    X = df[['times']].values
    y = df['accel'].values
    if return_X_y:
        return X, y
    return df

def coal(return_X_y=True):
    """Coal mining disaster data."""
    df = pd.read_csv(os.path.join(DATASETS_DIR, 'coal.csv'))
    X = df[['date']].values
    y = df['Unnamed: 0'].values  # This represents the count/event number
    if return_X_y:
        return X, y
    return df

def faithful(return_X_y=True):
    """Old Faithful geyser data."""
    df = pd.read_csv(os.path.join(DATASETS_DIR, 'faithful.csv'))
    X = df[['waiting']].values
    y = df['eruptions'].values
    if return_X_y:
        return X, y
    return df

def wage(return_X_y=True):
    """Wage data."""
    df = pd.read_csv(os.path.join(DATASETS_DIR, 'wage.csv'))
    X = df[['year', 'age', 'education']].values
    y = df['wage'].values
    if return_X_y:
        return X, y
    return df

def trees(return_X_y=True):
    """Tree data."""
    df = pd.read_csv(os.path.join(DATASETS_DIR, 'trees.csv'))
    X = df[['Girth', 'Height']].values
    y = df['Volume'].values
    if return_X_y:
        return X, y
    return df

def default(return_X_y=True):
    """Default data."""
    df = pd.read_csv(os.path.join(DATASETS_DIR, 'default.csv'))
    X = df[['balance', 'income']].values
    y = df['default'].values
    if return_X_y:
        return X, y
    return df

def cake(return_X_y=True):
    """Cake data."""
    df = pd.read_csv(os.path.join(DATASETS_DIR, 'cake.csv'))
    X = df[['temperature', 'recipe']].values
    y = df['angle'].values
    if return_X_y:
        return X, y
    return df

def hepatitis(return_X_y=True):
    """Hepatitis A data."""
    df = pd.read_csv(os.path.join(DATASETS_DIR, 'hepatitis_A_bulgaria.csv'))
    X = df[['age']].values
    y = df['hepatitis_A_positive'].values
    if return_X_y:
        return X, y
    return df

def head_circumference(return_X_y=True):
    """Head circumference data."""
    df = pd.read_csv(os.path.join(DATASETS_DIR, 'head_circumference.csv'))
    X = df[['age']].values
    y = df['head'].values
    if return_X_y:
        return X, y
    return df

def chicago(return_X_y=True):
    """Chicago air pollution data."""
    df = pd.read_csv(os.path.join(DATASETS_DIR, 'chicago.csv'))
    # Use available columns: pm10median, pm25median, o3median, so2median, tmpd
    X = df[['pm10median', 'pm25median', 'o3median', 'so2median', 'tmpd']].values
    y = df['death'].values
    if return_X_y:
        return X, y
    return df

def toy_classification(return_X_y=True, n=5000):
    """Generate toy classification data."""
    np.random.seed(42)
    X = np.random.randn(n, 2)
    y = (X[:, 0] + X[:, 1]**2 + np.random.randn(n) * 0.1 > 0).astype(int)
    if return_X_y:
        return X, y
    return pd.DataFrame(np.column_stack([X, y]), columns=['x1', 'x2', 'y'])

def toy_interaction(return_X_y=True, n=50000, stddev=0.1):
    """Generate toy interaction data."""
    np.random.seed(42)
    X = np.random.randn(n, 2)
    y = X[:, 0] * X[:, 1] + np.random.randn(n) * stddev
    if return_X_y:
        return X, y
    return pd.DataFrame(np.column_stack([X, y]), columns=['x1', 'x2', 'y'])

# List of available datasets
AVAILABLE_DATASETS = [
    'mcycle', 'coal', 'faithful', 'wage', 'trees', 'default', 
    'cake', 'hepatitis', 'head_circumference', 'chicago',
    'toy_classification', 'toy_interaction'
]

def list_datasets():
    """List all available datasets."""
    print("Available pyGAM datasets:")
    for dataset in AVAILABLE_DATASETS:
        print(f"  - {dataset}")
    return AVAILABLE_DATASETS

if __name__ == "__main__":
    # Test the datasets
    print("Testing pyGAM datasets...")
    for dataset_name in AVAILABLE_DATASETS:
        try:
            func = globals()[dataset_name]
            X, y = func(return_X_y=True)
            print(f"✓ {dataset_name}: X shape {X.shape}, y shape {y.shape}")
        except Exception as e:
            print(f"✗ {dataset_name}: Error - {e}")
