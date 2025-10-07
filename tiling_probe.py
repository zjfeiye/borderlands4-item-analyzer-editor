# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Akamoden
import argparse
from typing import List, Tuple, Dict, Set, Optional

# Import the same symbols your true encoder uses
from main import load_true_spec, QUARANTINE_BLOCKS
try:
    from main import _true_fits_capacity  # if exposed
except Exception:
    _true_fits_capacity = None

def enumerate_tilings(N: int,
                      allowed_l_by_b: Dict[int, List[int]],
                      mid_only: Set[Tuple[int,int]],
                      tail_only: Set[Tuple[int,int]],
                      quarantine: Set[Tuple[int,int]]) -> List[List[Tuple[int,int,str]]]:
    out: List[List[Tuple[int,int,str]]] = []
    stack: List[Tuple[int, List[Tuple[int,int,str]]]] = [(0, [])]
    while stack:
        used, seq = stack.pop()
        if used == N:
            if seq and seq[-1][2] == "tail":
                out.append(seq)
            continue
        rem = N - used
        # try all B that do not exceed rem
        for B, Ls in allowed_l_by_b.items():
            if B <= 0 or B > rem:
                continue
            for pos in ("mid", "tail") if B == rem else ("mid",):
                for L in set(Ls):
                    pair = (L, B)
                    if pair in quarantine:
                        continue
                    if pos == "tail" and pair in mid_only:
                        continue
                    if pos == "mid" and pair in tail_only:
                        continue
                    stack.append((used + B, seq + [(L, B, pos)]))
    # sort longer-L-first, fewer-blocks-first just to be pretty
    out.sort(key=lambda s: (sum(L for L,_,_ in s), len(s)))
    return out

def capacity_filter(seq: List[Tuple[int,int,str]], tail_bytes: bytes) -> bool:
    if _true_fits_capacity is None:
        return True  # can't check without helper
    # Greedy check: walk the sequence left-to-right consuming from the tail_bytes
    i = 0
    for L, B, pos in seq:
        chunk = tail_bytes[i:i+B]
        if len(chunk) != B:
            return False
        if not _true_fits_capacity(chunk, L, B):
            return False
        i += B
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("N", type=int, help="Remainder byte length to test")
    ap.add_argument("--with-bytes", type=str, default=None,
                    help="Hex string of the *last N bytes* from your item, to capacity-check")
    args = ap.parse_args()

    N = args.N
    true_spec, prefs = load_true_spec()
    allowed_l_by_b = {int(b): list(v) for b, v in true_spec["allowed_l_by_b"].items()}
    tail_only = set(tuple(x) for x in true_spec.get("tail_only", []))
    mid_only  = set(tuple(x) for x in true_spec.get("mid_only", []))
    quarantine = set(QUARANTINE_BLOCKS)

    tilings = enumerate_tilings(N, allowed_l_by_b, mid_only, tail_only, quarantine)
    print(f"[SUMMARY] Found {len(tilings)} structural tilings for N={N} "
          f"(ignoring capacity). Quarantined={len(quarantine)}")

    if not tilings:
        print("[DIAG] No structural tiling exists. Likely causes: over-aggressive quarantine.json, "
              "or tail/mid-only sets that forbid closing the sequence at B=N. "
              "Fix: loosen quarantine or adjust tail-only/mid-only for the needed (L,B).")
        return

    if args.with_bytes:
        try:
            tail_bytes = bytes.fromhex(args.with_bytes)
        except Exception as e:
            print(f"[WARN] Bad --with-bytes hex: {e}")
            return
        if len(tail_bytes) != N:
            print(f"[WARN] Provided bytes length {len(tail_bytes)} != N={N}")
            return
        ok = [seq for seq in tilings if capacity_filter(seq, tail_bytes)]
        print(f"[CAPACITY] {len(ok)}/{len(tilings)} tilings pass strict capacity for these bytes.")
        for i, seq in enumerate(ok[:10]):
            print(f"  #{i+1}: {seq}")
    else:
        for i, seq in enumerate(tilings[:20]):
            print(f"  #{i+1}: {seq}")
        if len(tilings) > 20:
            print(f"  ... ({len(tilings)-20} more)")

if __name__ == "__main__":
    main()
