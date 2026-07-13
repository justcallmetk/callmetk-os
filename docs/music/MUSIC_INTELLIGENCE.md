# CTK Music Intelligence

Version 0.7 introduces a local-first pipeline that turns catalog audio into reusable structured evidence.

## Pipeline

1. `ctk music analyze` extracts deterministic WAV metadata and lightweight signal features.
2. `ctk music cluster` standardizes those features and groups tracks with local K-Means.
3. `ctk music ep-build` converts a cluster into a TOAST recommendation requiring human approval.
4. `ctk music dna` summarizes recurring catalog characteristics.

The default implementation is free, offline, and deterministic. Optional `music` dependencies add a future path for richer BPM, key, spectral, and vocal analysis without changing the CLI contract.

## Boundaries

- The system recommends; the creator approves.
- Raw audio stays outside Git.
- Analysis results may be stored in CSV and Creative Library metadata.
- Unsupported formats are recorded honestly rather than guessed.
- Mood, lyrical theme, and creative-domain assignment remain enrichment tasks, not objective facts.
