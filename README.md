# BL4Tools (Essentials) — strict/TRUE encoder–decoder & editors

**Status:** maintenance mode. PRs welcome; no bundled game assets.  
**License:** MIT (see LICENSE). Sources include SPDX headers.

## Included tools
- `main.py` — strict/TRUE encoder–decoder + Base‑85 block rules (BL4 alphabet).
- `round_trip.py` — corpus round‑trip test, inspectors, compare, edit helpers.
- `bit_inspect.py` — bitstream + byte↔char block mapping inspectors.
- `multi_patch_true.py` — apply multiple raw byte edits with TRUE/strict/hybrid re‑encode.
- `tiling_probe.py` — enumerate legal tilings for remainder N; capacity check with bytes.
- `pin_remainder_helper.py` — compute remainder N for an edit index and suggest a DP seq.
- `batch_byte_inspect.py` — batch dump per‑byte tables for many serials into one CSV.

> Note: filenames are case‑sensitive on some platforms. The patcher is `multi_patch_true.py` and the probe is `tiling_probe.py`.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt  # if you keep one; otherwise just use system Python 3.10+

# Inspect a serial's bytes + zones (mid/tail)
python round_trip.py --inspect-bytes "@Ug..." --fmt both

# Bit dump and block mapping
python bit_inspect.py --bitdump "@Ug..." --bitdump-limit 512
python bit_inspect.py --inspect "@Ug..."

# Apply multiple tail edits with full TRUE re‑encode
python multi_patch_true.py --serial "@Ug..." --patch "25=0x00,26=0x00" --encode-mode true

# Plan/pin a remainder N for a planned edit
python pin_remainder_helper.py --serial "@Ug..." --index 18 --out canonical_snippet.json

# Explore tilings for N with capacity check
python tiling_probe.py 17 --with-bytes 0011aa...

# Batch inspect a list of serials to CSV
python batch_byte_inspect.py --serial-file serials.txt --out byte_inspect.csv
```

## Concepts (very short)
- **Blocks:** (L→B) digit→byte packs; e.g., 25→20, 41→33, 5→4, 2→2.  
- **Zones:** *mid* vs *tail*; tail has extra constraints (e.g., 3‑byte/2‑digit quirk).  
- **TRUE encoder:** canonical overrides + DP to mirror game choices 1:1.  
- **Strict encoder:** re‑encode with the exact tiling recovered by strict decode.

## Legal
No game assets, SDKs, or dumps are included. For research & interoperability only. You are responsible for your game’s ToS/EULA.

---
Maintained by Akamoden
