# Bonus Features

This document summarises the experimental endpoints that extend the core face-profiling service.

For full request/response examples see the dedicated sections in **[API Reference](api_reference.md#3-bonus-endpoints)**.

---

## Endpoints

| Path | Summary |
|------|---------|
| `POST /api/v1/verify-face` | Generate a profile and perform a stub liveness check |
| `POST /api/v1/detect-deepfake` | Return a confidence score indicating whether the image is likely a deepfake |

---

### Verify Face

The endpoint returns the same `Profile` schema used by `/create-profile` but with an additional description indicating liveness.

### Detect Deepfake

Returns a JSON object with two keys:

```json
{
  "is_deepfake": false,
  "confidence": 0.42,
  "description": "Likely genuine"
}
```

Confidence is a deterministic pseudo-random value for now and will be replaced by a real detector model in future iterations. 