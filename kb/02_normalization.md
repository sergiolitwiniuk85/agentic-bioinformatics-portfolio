# Normalization of single-cell count data

Count data must be normalized to compare cells with different sequencing depths.

## Steps
- Normalize total counts per cell to a target sum (e.g. 10,000).
- Apply log1p to stabilize variance.
- Select highly variable genes (top 2,000) for downstream dimensionality reduction.
