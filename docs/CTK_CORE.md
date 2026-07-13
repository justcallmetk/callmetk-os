# CTK Core v0.6.0

CTK Core introduces shared configuration, AI cost controls, TOAST decisions, Creative Library indexing, and Workspace status.

## AI cost modes

```bash
ctk ai init
ctk ai mode free
ctk ai mode balanced --budget 10
ctk ai mode quality --budget 25
ctk ai status
ctk ai providers
ctk ai route coding
```

The default mode is `free`, paid fallback is disabled, and human approval is required for paid recommendations.

## Creative Library

The library stores media outside the source-code repository.

```bash
ctk library init ~/CallMeTK/callmetk-library
ctk library scan ~/CallMeTK/callmetk-library
ctk library status
ctk library validate
```

The generated catalog is stored at `catalog/library.csv` and contains SHA-256 checksums, stable asset IDs, relative paths, types, sizes, tags, and relationships.

## Workspace

```bash
ctk workspace init ~/CallMeTK/workspace
ctk workspace status
```

The first workspace implementation stores a lightweight registry that later versions can use for projects, libraries, releases, security, and CTK Studio.

## TOAST

Provider recommendations use the common TOAST decision structure:

- target
- options
- selection
- confidence
- reasoning
- evidence
- alternatives
- estimated cost
- approval requirement
