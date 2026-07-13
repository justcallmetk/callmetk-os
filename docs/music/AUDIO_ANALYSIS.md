# Audio Analysis Standard

The core analyzer supports PCM WAV files without paid APIs. It records duration, sample rate, channels, bit depth, peak, RMS, energy, and a lightweight brightness proxy. Analysis is capped to an initial window for responsive catalog scans.

MP3, FLAC, AIFF, M4A, tempo, key, and advanced descriptors are represented in the schema but may require the optional music dependency group:

```bash
python -m pip install -e '.[music]'
```

Unsupported analysis is marked `unsupported`; errors are marked `error`. CTK OS must not fabricate values.
