#!/usr/bin/env python3
"""
Dask PCA Implementation

A standalone implementation of PCA for Dask arrays that handles NaN values.
This module provides efficient PCA computation for large datasets using Dask.
"""

import dask.array as da
import numpy as np
import matplotlib.pyplot as plt


def dask_pca(X, n_components=None):
    """
    Compute PCA for a dask array X (samples x features).
    Returns principal components and explained variances.
    
    Parameters:
        X: dask.array.Array, shape (n_samples, n_features)
        n_components: int or None, number of PCs to compute (default: all)
    Returns:
        components_: principal axes (n_components, n_features)
        explained_variances_: variances explained by each PC (all components, i.e. n_features,)
        mean_: mean of X (n_features,)
    """
    # Use nanmean to center, ignoring NaNs
    mean_ = da.nanmean(X, axis=0)
    Xc = X - mean_

    # For covariance, handle NaNs: for each pair of features, compute the mean excluding any rows with NaN in either feature

    # We'll compute the valid-count matrix and the nan-aware cross-products via masked arrays

    # Compute dot product (ignoring NaNs)
    # Use masked_arrays to compute sums where both values are finite
    def nan_cov(a):
        # a: (n_samples, n_features)
        valid = da.isfinite(a)
        counts = da.matmul(valid.T, valid)
        
        # Handle case where counts might be 0 or 1
        counts = da.where(counts <= 1, 2, counts)
        
        # Use nan_to_num to replace NaN with 0 for covariance computation
        a_clean = da.nan_to_num(a)
        product = da.matmul(a_clean.T, a_clean)
        cov = product / (counts - 1)
        
        # Ensure covariance matrix is symmetric and positive semi-definite
        cov = (cov + cov.T) / 2
        
        return cov

    cov = nan_cov(Xc)
    # Convert to numpy for eigendecomposition
    cov = cov.compute()

    # Add small regularization for numerical stability
    cov = cov + np.eye(cov.shape[0]) * 1e-10

    # Eigen decomposition
    try:
        eigvals, eigvecs = np.linalg.eigh(cov)
    except np.linalg.LinAlgError:
        # If eigh fails, try with SVD
        try:
            U, s, Vt = np.linalg.svd(cov, full_matrices=False)
            eigvals = s ** 2
            eigvecs = U
        except np.linalg.LinAlgError:
            # Final fallback: use sklearn PCA
            from sklearn.decomposition import PCA
            X_clean = da.nan_to_num(X).compute()
            # Fit PCA with all components to get all explained variances
            pca_full = PCA()
            pca_full.fit(X_clean)
            all_explained_variances = pca_full.explained_variance_
            
            # Get only the requested number of components
            if n_components is not None:
                pca = PCA(n_components=n_components)
                pca.fit(X_clean)
                eigvecs = pca.components_.T
            else:
                eigvecs = pca_full.components_.T
            
            mean_ = pca_full.mean_
            return eigvecs, all_explained_variances, mean_
    
    # Sort eigenvalues & eigenvectors in descending order
    idx = eigvals.argsort()[::-1]
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]

    # Store all eigenvalues (explained variances) before truncating eigenvectors
    all_explained_variances = eigvals.copy()

    if n_components is not None:
        eigvecs = eigvecs[:, :n_components]

    # eigvecs: columns are principal axes
    # Return all explained variances, but only requested number of components
    return eigvecs.T, all_explained_variances, mean_.compute()


def dask_pca_transform(X, components_, mean_):
    """
    Transform data using computed PCA components.
    
    Parameters:
        X: dask.array.Array, shape (n_samples, n_features)
        components_: principal axes (n_components, n_features)
        mean_: mean of X (n_features,)
    Returns:
        X_transformed: transformed data (n_samples, n_components)
    """
    # Center the data
    Xc = X - mean_
    
    # Transform using principal components
    X_transformed = da.matmul(Xc, components_.T)
    
    return X_transformed


def dask_pca_inverse_transform(X_transformed, components_, mean_):
    """
    Inverse transform PCA data back to original space.
    
    Parameters:
        X_transformed: transformed data (n_samples, n_components)
        components_: principal axes (n_components, n_features)
        mean_: mean of X (n_features,)
    Returns:
        X_reconstructed: reconstructed data (n_samples, n_features)
    """
    # Transform back to original space
    X_reconstructed = da.matmul(X_transformed, components_) + mean_
    
    return X_reconstructed


def dask_pca_explained_variance_ratio(explained_variances_):
    """
    Calculate explained variance ratio for each principal component.
    
    Parameters:
        explained_variances_: variances explained by each PC
    Returns:
        explained_variance_ratio_: ratio of explained variance for each PC
    """
    total_variance = da.sum(explained_variances_)
    explained_variance_ratio_ = explained_variances_ / total_variance
    
    return explained_variance_ratio_


def plot_mean_std(df, title="Mean and Std Dev of TAVG by Day of Year", ylabel="TAVG (°C)", figsize=(6, 3)):
    """
    Compute, plot, and return the mean and std dev by day-of-year columns for a TAVG dataframe.
    Assumes columns are named as 'day_1', 'day_2', ..., 'day_365'.
    
    Parameters:
        df: DataFrame with day columns
        title: Plot title
        ylabel: Y-axis label
        figsize: Figure size tuple (width, height), default (6, 3)
    
    Returns:
        daily_means, daily_stds
    """
    # Select columns for each day of the year (assuming columns named day_1 to day_365)
    day_cols = [col for col in df.columns if col.startswith('day_') and col[4:].isdigit()]
    day_cols_sorted = sorted(day_cols, key=lambda x: int(x.split('_')[1]))

    # Calculate mean and std for each day of year across all stations/years
    # If input is a Dask DataFrame, use .compute(); if it's already a pandas DataFrame, do nothing.
    # Here, we assume df may be Dask or pandas; check and convert if needed.
    if hasattr(df, 'compute'):
        df = df.compute()
    daily_means = df[day_cols_sorted].mean()
    daily_stds = df[day_cols_sorted].std()

    days = np.arange(1, len(day_cols_sorted) + 1)

    plt.figure(figsize=figsize)
    plt.plot(days, daily_means, label='Mean')
    plt.fill_between(days, daily_means-daily_stds, daily_means+daily_stds, color='b', alpha=0.2, label='±1 Std Dev')

    # Define month boundaries for labels (non-leap year)
    month_boundaries = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', '']

    plt.xticks(month_boundaries, month_labels)
    plt.xlim(1, 365)
    plt.xlabel('Month')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()
    return daily_means, daily_stds


def plot_mean_and_pcs(data, n_components=3, title="Mean and Principal Components", 
                     xlabel="Time", ylabel="Signal Value", signal_name="Signal",
                     x_values=None, figsize=(6, 3)):
    """
    Plot the mean signal and top K principal components for any signal data.
    
    Parameters:
        data: array-like, shape (n_samples, n_features)
            Input data where rows are samples and columns are features
        n_components (int): Number of principal components to plot (default: 3)
        title (str): Plot title
        xlabel (str): X-axis label
        ylabel (str): Y-axis label for the mean signal
        signal_name (str): Name of the signal for legend
        x_values: array-like, optional
            X-axis values (e.g., days, time points). If None, uses range(1, n_features+1)
        figsize (tuple): Figure size (width, height)
    
    Returns:
        tuple: (mean, components, explained_variances)
    """
    import dask.array as da
    import numpy as np
    import matplotlib.pyplot as plt
    
    # Convert to dask array if needed
    if not isinstance(data, da.Array):
        data = da.from_array(data, chunks=(128, -1))
    
    # Run PCA
    components, explained_variances, mean = dask_pca(data, n_components=n_components)
    
    # Compute results
    mean_np = mean.compute() if hasattr(mean, 'compute') else mean
    components_np = components.compute() if hasattr(components, 'compute') else components
    
    # Set up x-axis values
    if x_values is None:
        x_values = np.arange(1, len(mean_np) + 1)
    
    # Create the plot
    fig, ax1 = plt.subplots(figsize=figsize)
    
    # Plot the mean signal
    mean_line, = ax1.plot(x_values, mean_np, color='tab:blue', label=f'Mean {signal_name}')
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel, color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    
    # Plot principal components on secondary y-axis
    ax2 = ax1.twinx()
    pc_colors = ['tab:red', 'tab:orange', 'tab:green', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
    pc_labels = [f'PC{i+1}' for i in range(n_components)]
    pc_lines = []
    
    for i in range(n_components):
        color = pc_colors[i % len(pc_colors)]
        line, = ax2.plot(x_values, components_np[i], color=color, 
                        label=pc_labels[i], linestyle='--')
        pc_lines.append(line)
    
    ax2.set_ylabel('PC Value (a.u.)', color='tab:gray')
    ax2.tick_params(axis='y', labelcolor='tab:gray')
    
    # Add legends
    lines = [mean_line] + pc_lines
    labels = [f'Mean {signal_name}'] + pc_labels
    ax1.legend(lines, labels, loc='upper right')
    
    # Set title
    plt.title(title)
    plt.tight_layout()
    plt.show()
    
    return mean_np, components_np, explained_variances


# Example usage
if __name__ == "__main__":
    # Create sample data
    import dask.array as da
    
    # Generate random data with some NaN values
    np.random.seed(42)
    n_samples, n_features = 1000, 50
    X = da.random.random((n_samples, n_features))
    
    # Add some NaN values
    nan_mask = da.random.random((n_samples, n_features)) < 0.1
    X = da.where(nan_mask, np.nan, X)
    
    print(f"Sample data shape: {X.shape}")
    print(f"Number of NaN values: {da.isnan(X).sum().compute()}")
    
    # Perform PCA
    components_, explained_variances_, mean_ = dask_pca(X, n_components=3)
    
    print(f"Components shape: {components_.shape}")
    print(f"Explained variances: {explained_variances_}")
    
    # Calculate explained variance ratio
    explained_variance_ratio_ = dask_pca_explained_variance_ratio(explained_variances_)
    print(f"Explained variance ratio: {explained_variance_ratio_.compute()}")
    
    # Transform data
    X_transformed = dask_pca_transform(X, components_, mean_)
    print(f"Transformed data shape: {X_transformed.shape}")
    
    # Inverse transform
    X_reconstructed = dask_pca_inverse_transform(X_transformed, components_, mean_)
    print(f"Reconstructed data shape: {X_reconstructed.shape}")
