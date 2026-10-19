# Xenium subcellular spatial analysis

Xenium is an imaging-based, subcellular-resolution spatial transcriptomics platform.

## Characteristics
- Single-cell resolution: each cell is segmented individually (not spots).
- Transcripts are localized with sub-micron coordinates.
- Includes a tissue morphology image (DAPI / immunofluorescence).

## Analysis steps
- Read the cell-feature matrix and cell centroids.
- QC: filter cells with too few transcripts.
- Normalize and log-transform counts.
- Cluster cells (Leiden) to identify cell types.
- Plot cells colored by cluster at their spatial coordinates.
