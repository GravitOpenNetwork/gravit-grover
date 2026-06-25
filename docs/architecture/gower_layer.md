# Gower Similarity Layer

## Overview

The Gower Similarity Layer provides geometric representation of the hypothesis space. It computes pairwise similarities between hypotheses using Gower's general similarity coefficient, which handles mixed data types.

## Mathematical Foundation

### Gower Similarity Coefficient

For two observations i and j, the Gower similarity is:
S(i, j) = (Σ_k w_k · s_k(i, j)) / (Σ_k w_k)

Where:
- w_k: Weight for feature k
- s_k: Similarity for feature k

### Feature Types

#### Numeric Features
s_k(i, j) = 1 - |x_ik - x_jk| / R_k

Where R_k is the range of feature k.

#### Categorical Features
s_k(i, j) = {
1, if x_ik = x_jk
0, otherwise
}

#### Ordinal Features
s_k(i, j) = 1 - |rank(x_ik) - rank(x_jk)| / (R_k - 1)

#### Binary Features
s_k(i, j) = {
1, if x_ik = x_jk
0, otherwise
}

## Distance Computation

### Gower Distance
d(i, j) = 1 - S(i, j)

### Properties
- **Non-negativity**: d(i, j) ≥ 0
- **Symmetry**: d(i, j) = d(j, i)
- **Bounded**: 0 ≤ d(i, j) ≤ 1

## Similarity Matrix

### Construction
S = [[S_11, S_12, ..., S_1n],
[S_21, S_22, ..., S_2n],
[... ],
[S_n1, S_n2, ..., S_nn]]

### Properties
- **Diagonal**: S_ii = 1
- **Symmetric**: S_ij = S_ji
- **Positive semi-definite**: For certain kernels

## Hypothesis Space Geometry

### Embedding

Hypotheses embedded in similarity space:
φ: H → ℝᵈ

Where d is the number of features.

### Distance Matrix
D_ij = d(i, j) = 1 - S_ij

### Similarity Clustering

Group hypotheses by similarity:

```python
from sklearn.cluster import AgglomerativeClustering

def cluster_hypotheses(similarity_matrix: np.ndarray,
                       n_clusters: int = 5) -> np.ndarray:
    """
    Cluster hypotheses based on similarity.
    """
    distance_matrix = 1 - similarity_matrix
    clustering = AgglomerativeClustering(
        n_clusters=n_clusters,
        affinity='precomputed',
        linkage='average'
    )
    return clustering.fit_predict(distance_matrix)
```
## Consistency Scoring
### Definition
Consistency of hypothesis h with reference set R:

C(h, R) = (1/|R|) Σ_{r∈R} S(h, r)
## Applications
Outlier Detection: Low consistency indicates anomaly

Quality Filtering: Keep only consistent hypotheses

Weight Adjustment: Use consistency as weight factor

### Implementation
```python
def compute_consistency(hypothesis: np.ndarray,
                       reference_set: np.ndarray,
                       gower: GowerDistance) -> float:
    """
    Compute consistency of a hypothesis.
    """
    scores = []
    for ref in reference_set:
        scores.append(gower.compute_similarity(hypothesis, ref))
    return np.mean(scores)
```
## Weighted Gower
### Feature Weighting

S_weighted(i, j) = (Σ_k w_k · s_k(i, j)) / (Σ_k w_k)
### Weight Selection
Uniform: w_k = 1

Expert: Based on domain knowledge

Learned: Optimized through training

### Adaptive Weights
Weights can be learned through iterations:

w_k(t+1) = w_k(t) · exp(η · ∂L/∂w_k)
## Applications
1. Hypothesis Similarity
```python
# Example: Computing hypothesis similarity
gower = GowerDistance()
hypothesis_features = extract_features(hypotheses)
similarities = gower.compute_similarity_matrix(hypothesis_features)
```
2. Hypothesis Clustering
```python
Example: Clustering similar hypotheses
clusters = cluster_hypotheses(similarities, n_clusters=3)
```
3. Hypothesis Ranking
```python
# Example: Ranking hypotheses by consistency
consistency_scores = compute_all_consistencies(hypotheses, similarities)
ranked_hypotheses = hypotheses[np.argsort(consistency_scores)]
```
## Performance Optimization
### Memoization
```python
class GowerDistance:
    def __init__(self):
        self.cache = {}

    def compute_similarity(self, i, j):
        key = (i, j)
        if key in self.cache:
            return self.cache[key]
        # Compute similarity
        result = self._compute_similarity(i, j)
        self.cache[key] = result
        return result
```
### Vectorization
```python
def compute_similarity_matrix_vectorized(data: np.ndarray) -> np.ndarray:
    """
    Vectorized computation for numeric features.
    """
    n_samples = len(data)
    S = np.zeros((n_samples, n_samples))

    for k in range(data.shape[1]):
        range_k = np.max(data[:, k]) - np.min(data[:, k])
        if range_k > 0:
            # Vectorized distance computation
            diff = data[:, k:k+1] - data[:, k:k+1].T
            S_k = 1 - np.abs(diff) / range_k
            S += S_k

    return S / data.shape[1]
```

## References
1. Gower, J. C. (1971). A general coefficient of similarity and some of its properties. Biometrics.
2. Kaufman, L., & Rousseeuw, P. J. (2009). Finding groups in data: An introduction to cluster analysis.
3. Legendre, P., & Legendre, L. (2012). Numerical ecology.
