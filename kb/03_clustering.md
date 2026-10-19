# Clustering and differential expression

Clustering groups cells by transcriptional similarity.

## Steps
- Scale data and run PCA (50 components).
- Build a k-nearest-neighbor graph (15 neighbors).
- Run Leiden clustering to assign communities.
- Use Wilcoxon rank-sum test to find marker genes per cluster.
