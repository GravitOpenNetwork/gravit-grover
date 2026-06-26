# Consensus Mathematics

## Overview

Gravit Grover achieves distributed consensus through a combination of gossip protocols and mixing matrices. This document provides the mathematical foundation for convergence guarantees.

## Convergence Framework

### Distributed Consensus Problem

Given a network of N nodes, each with vector x_i, we want all nodes to converge to the same vector x*:

```math
lim_{t→∞} x_i(t) = x*, ∀i ∈ {1,...,N}
```

### Graph Model

Network topology represented as undirected graph G = (V, E):
- V: Set of nodes
- E: Set of edges (communication links)
- N: Adjacency matrix

## Gossip Consensus

### Push-Pull Gossip

**Push Phase:**

```math
x_i(t+1) = x_i(t) - α(x_i(t) - x_j(t))
```

**Pull Phase:**

```math
x_j(t+1) = x_j(t) + α(x_i(t) - x_j(t))
```

**Combined:**

```math
x_i(t+1) = (1 - α)x_i(t) + α(x_j(t))
x_j(t+1) = (1 - α)x_j(t) + α(x_i(t))
```

### Convergence Rate

The convergence rate is determined by the spectral gap of the mixing matrix W:

```math
||x(t) - x||₂² ≤ (1 - λ₂)ᵗ ||x(0) - x||₂²
```

Where:
- λ₂: Second largest eigenvalue
- t: Number of iterations
- x*: Consensus value

## Mixing Matrices

### Metropolis-Hastings Matrix

```math
W_ij = {
1/(1 + max(d_i, d_j)), if (i,j) ∈ E
0, if (i,j) ∉ E and i ≠ j
1 - Σ_j W_ij, if i = j
}
```

### Heat Kernel Matrix

```math
W = exp(-βL)
```

Where L is the graph Laplacian.

### Symmetric Matrix

```math
W_ij = {
1/(d_i + 1), if (i,j) ∈ E
0, otherwise
}
```

## Spectral Properties

### Graph Laplacian

```math
L = D - A
```

Where:
- D: Degree matrix
- A: Adjacency matrix

### Eigenvalues

```math
0 = λ₁ ≤ λ₂ ≤ ... ≤ λ_N
```

**Spectral Gap:**

```math
γ = λ₂
```

### Fiedler Value

The second smallest eigenvalue λ₂ determines the graph's connectivity.

### Convergence Speed

The spectral gap determines convergence speed:

```math
log ||x(t) - x*||₂₂ ≈ -γ t
```

## Probability Distributions

### Node Beliefs

Each node maintains a probability distribution:
P_i(h) = probability that hypothesis h is correct

### Consensus Distribution
```math
P*(h) = argmax Σ_i P_i(h)
```

### KL Divergence
```math
D_KL(P_i || P_j) = Σ_h P_i(h) log(P_i(h)/P_j(h))
```

## Convergence Proof

### Theorem

Under the Metropolis-Hastings mixing matrix, the network achieves consensus with probability 1.

### Proof Sketch

1. Define Lyapunov function:
```math
V(t) = Σ_i ||x_i(t) - x*||₂²
```

2. Show V(t+1) ≤ (1 - γ)V(t):
```math
V(t+1) = V(t) - 2Σ_i Σ_j W_ij ||x_i - x_j||₂²
```

3. By Poincaré inequality:
```math
Σ_i Σ_j W_ij ||x_i - x_j||₂² ≥ γ V(t)
```

4. Therefore:
```math
V(t) ≤ (1 - γ)ᵗ V(0)
```

5. Thus:

```math
lim_{t→∞} V(t) = 0
```

### Convergence Time

```math
T_consensus = O(log(N) / γ)
```

## Consensus with Noisy Messages

### Noise Model

```math
y_i(t) = x_i(t) + η_i(t)
```

Where η_i(t) is zero-mean noise.

### Error Bounds

```math
||x(t) - x||₂² ≤ (1 - γ)ᵗ ||x(0) - x||₂² + σ²/γ
```

Where σ² is the noise variance.

## Multi-Consensus

### Multiple Parameters

Consensus on multiple parameters simultaneously:

```math
x_i(t) ∈ Rᵈ
```

### Vector Consensus

```math
||x_i(t+1) - x||₂² ≤ (1 - γ)ᵗ ||x_i(0) - x||₂²
```

## Practical Implementation

### Matrix Construction

```python
def create_mixing_matrix(adjacency: np.ndarray) -> np.ndarray:
    """
    Create Metropolis-Hastings mixing matrix.
    """
    n = len(adjacency)
    W = np.zeros((n, n))

    for i in range(n):
        degree_i = np.sum(adjacency[i])
        for j in range(n):
            if adjacency[i][j]:
                degree_j = np.sum(adjacency[j])
                W[i][j] = 1 / (1 + max(degree_i, degree_j))

        W[i][i] = 1 - np.sum(W[i])

    return W
```

### Convergence Monitoring
```python
def check_convergence(state: np.ndarray, tolerance: float = 1e-6) -> bool:
    """
    Check if consensus has been achieved.
    """
    mean = np.mean(state, axis=0)
    diff = np.max(np.abs(state - mean))
    return diff < tolerance
```

## Optimizations

### Push-Sum Consensus

```math
x_i(t+1) = W_ii x_i(t) + Σ_j W_ij x_j(t)
```

### Linear Consensus

```math
x_i(t+1) = x_i(t) + ε Σ_j (x_j(t) - x_i(t))
```

## References

* Boyd, S., Ghosh, A., Prabhakar, B., & Shah, D. (2006). Randomized gossip algorithms. IEEE Transactions on Information Theory.
* Kempe, D., Dobra, A., & Gehrke, J. (2003). Gossip-based computation of aggregate information.
* Xiao, L., & Boyd, S. (2004). Fast linear iterations for distributed averaging.
