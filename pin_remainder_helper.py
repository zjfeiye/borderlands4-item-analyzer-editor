# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Akamoden
#!/usr/bin/env python3
"""
pin_remainder_helper.py

Automates:
  1) Compute remainder N for a planned byte edit (i, T -> N = T - i)
  2) Try to capture a suitable DP sequence ("seq") for that N:
     - Prefer pulling a seq from a prior run.log (if it contains decision traces)
     - Otherwise, validate candidates via `tiling_probe.py N --with-bytes <hex>`
       using the *post-edit* last-N bytes (you supply the serial before editing,
       and the helper extracts bytes from `round_trip.py --inspect-bytes` output).

This script does **not** modify any project files. It prints a JSON snippet you
could add to canonical_overrides.json **only if** you choose to.

USAGE (Windows PowerShell examples):
  # Get N and probe a seq candidate using your current serial + index
  python pin_remainder_helper.py ^
    --serial "@Ugx...yourSerial..." ^
    --index 18

  # Also scan an existing run.log for any seq lines (optional)
  python pin_remainder_helper.py ^
    --serial "@Ugx...yourSerial..." ^
    --index 18 ^
    --log run.log

  # Emit a JSON snippet file with the best validated seq found (optional)
  python pin_remainder_helper.py ^
    --serial "@Ugx...yourSerial..." ^
    --index 18 ^
    --out canonical_snippet.json

REQUIREMENTS (assumes your existing tools):
  - round_trip.py (for --inspect-bytes)
  - tiling_probe.py (for N probing/validation)
  Both should be on the PATH or in the working directory.

Notes:
  - If your program currently prints zero decision traces (100% match), --log may
    not contain any 'seq'. In that case we rely on tiling_probe validation.
  - We parse bytes (hex) from `--inspect-bytes` output lines that look like:
        "   17  148/94   ..."
    and collect the "/HH" column. If your format differs, see regexes below.
"""

import argparse
import json
import re
import subprocess
from typing import List, Tuple, Optional, Dict, Any

def run_cmd(cmd: List[str]) -> str:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.stdout

def parse_inspect_output_for_bytes_and_blocks(text: str) -> Tuple[List[int], Optional[List[Tuple[int,int,str]]]]:
    """
    Extract bytes (as ints) and block tuples from round_trip.py --inspect-bytes output.

    Expected byte lines contain something like:
        "   17       148/94    ..."
    We'll parse the hex (94) as a byte.
    Blocks line might look like:
        "blocks: [(26, 21, 'mid'), (6, 5, 'tail')]"
    """
    bytes_list: List[int] = []
    # Match lines like: optional spaces, idx, spaces, dec/HEX
    byte_line_re = re.compile(r"^\s*\d+\s+(\d+)/([0-9A-Fa-f]{2})\b")
    for line in text.splitlines():
        m = byte_line_re.match(line)
        if m:
            hex_byte = m.group(2)
            try:
                bval = int(hex_byte, 16)
                bytes_list.append(bval)
            except ValueError:
                pass

    blocks: Optional[List[Tuple[int,int,str]]] = None
    blocks_re = re.compile(r"blocks:\s*\[(.*?)\]")
    m = blocks_re.search(text)
    if m:
        inner = m.group(1)
        # find all tuples like (L, B, 'mid'|'tail')
        tup_re = re.compile(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*'((?:mid|tail))'\s*\)")
        blocks = [(int(L), int(B), pos) for (L, B, pos) in tup_re.findall(inner)]

    return bytes_list, blocks

def hex_of_last_n_bytes(bytes_list: List[int], N: int) -> str:
    if N <= 0 or N > len(bytes_list):
        raise ValueError(f"N={N} out of range for T={len(bytes_list)}")
    tail = bytes_list[-N:]
    return "".join(f"{b:02x}" for b in tail)

def parse_log_for_sequences(log_text: str, N: Optional[int] = None) -> List[List[Tuple[int,int,str]]]:
    """
    Grep any 'seq' arrays from a run.log. Optionally filter for those that
    declare the same remainder N (if the log includes that detail). Since log
    format can vary, we keep it best-effort.
    We accept sequences of tuples (L,B,'mid|tail').
    """
    seqs: List[List[Tuple[int,int,str]]] = []
    # Look for "seq": [(26, 21, 'mid'), (6, 5, 'tail')]
    seq_re = re.compile(r"'seq'\s*:\s*\[(.*?)\]")
    tup_re = re.compile(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*'((?:mid|tail))'\s*\)")

    for m in seq_re.finditer(log_text):
        inner = m.group(1)
        tuples = tup_re.findall(inner)
        if tuples:
            seq = [(int(L), int(B), pos) for (L, B, pos) in tuples]
            seqs.append(seq)

    # Optional: try to correlate by N using nearby 'N' or 'remainder' mentions
    if N is not None and seqs:
        filtered: List[List[Tuple[int,int,str]]] = []
        lines = log_text.splitlines()
        for i, m in enumerate(seq_re.finditer(log_text)):
            seq_inner = m.group(1)
            # Peek around this occurrence for a number like "N=..." or "remainder 8"
            start_idx = max(0, log_text.rfind("\n", 0, m.start()))
            end_idx = log_text.find("\n", m.end())
            context = log_text[start_idx:end_idx if end_idx != -1 else len(log_text)]
            # simple N scan
            n_found = re.findall(r"\bN\s*=\s*(\d+)\b|\bremainder\s+(\d+)\b", context)
            if n_found:
                nums = [int(x or y) for (x, y) in n_found]
                if N in nums:
                    tuples = tup_re.findall(seq_inner)
                    if tuples:
                        filtered.append([(int(L), int(B), pos) for (L, B, pos) in tuples])
        if filtered:
            return filtered

    return seqs

def unique_seqs(seqs: List[List[Tuple[int,int,str]]]) -> List[List[Tuple[int,int,str]]]:
    seen = set()
    uniq = []
    for s in seqs:
        key = tuple(s)
        if key not in seen:
            seen.add(key)
            uniq.append(s)
    return uniq

def run_tiling_probe(N: int, last_n_hex: str, cmd_template: Optional[str] = None) -> List[Tuple[int,int,str]]:
    """
    Call tiling_probe.py to find/validate a sequence for N with exact bytes.
    We attempt to parse a seq-like list from its output.
    """
    if cmd_template is None:
        # Default invocation
        cmd = ["python", "tiling_probe.py", str(N), "--with-bytes", last_n_hex]
    else:
        # Allow a custom command template with placeholders
        cmd_string = cmd_template.format(N=N, HEX=last_n_hex)
        # naive split respecting quotes could be implemented, but we expect simple usage
        cmd = cmd_string.split()

    out = run_cmd(cmd)

    # Try to parse a sequence from output
    tup_re = re.compile(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*'((?:mid|tail))'\s*\)")
    tuples = tup_re.findall(out)
    if tuples:
        return [(int(L), int(B), pos) for (L, B, pos) in tuples]

    # If not found, just return empty; caller can show the raw output for debugging
    return []

def main():
    ap = argparse.ArgumentParser(description="Compute remainder N and suggest a DP seq for pinning.")
    ap.add_argument("--serial", help="Pre-edit serial string (used to inspect bytes).")
    ap.add_argument("--index", type=int, required=True, help="Index i (first byte you will change). 0-based.")
    ap.add_argument("--log", help="Optional run.log to scan for pre-existing seq lines.")
    ap.add_argument("--inspect-cmd", default=None,
                    help='Custom inspect command template; use {SERIAL}. '
                         'Default: python round_trip.py --inspect-bytes "{SERIAL}" --start 0 --end 99999')
    ap.add_argument("--tiling-probe-cmd", default=None,
                    help='Custom tiling probe command template; use {N} and {HEX}. '
                         'Default: python tiling_probe.py {N} --with-bytes {HEX}')
    ap.add_argument("--out", help="Optional path to write a JSON snippet (e.g., canonical_snippet.json)")
    args = ap.parse_args()

    if not args.serial:
        print("[ERROR] --serial is required to extract bytes with --inspect-bytes.", file=sys.stderr)
        sys.exit(2)

    # 1) Inspect bytes for T and blocks
    if args.inspect_cmd:
        inspect_cmd = args.inspect_cmd.format(SERIAL=args.serial)
        cmd = inspect_cmd.split()
    else:
        cmd = ["python", "round_trip.py", "--inspect-bytes", args.serial, "--start", "0", "--end", "99999"]

    inspect_out = run_cmd(cmd)
    bytes_list, blocks = parse_inspect_output_for_bytes_and_blocks(inspect_out)

    if not bytes_list:
        print("[ERROR] Could not parse bytes from --inspect-bytes output. "
              "Ensure the output includes lines like '  17  148/94 ...'", file=sys.stderr)
        print("--- inspect output (first 80 lines) ---")
        print("\n".join(inspect_out.splitlines()[:80]))
        sys.exit(3)

    T = len(bytes_list)
    i = args.index
    if i < 0 or i >= T:
        print(f"[ERROR] index i={i} out of range for total bytes T={T}", file=sys.stderr)
        sys.exit(4)

    N = T - i
    print(f"[INFO] Total bytes (T): {T}")
    print(f"[INFO] Planned edit index (i): {i}")
    print(f"[INFO] Remainder (N = T - i): {N}")

    last_hex = hex_of_last_n_bytes(bytes_list, N)
    print(f"[INFO] Last-N bytes (hex): {last_hex}")

    # 2) Try to pull seqs from a run.log (optional)
    seqs_from_log: List[List[Tuple[int,int,str]]] = []
    if args.log:
        try:
            with open(args.log, "r", encoding="utf-8", errors="ignore") as f:
                log_text = f.read()
            seqs_from_log = parse_log_for_sequences(log_text, N=N)
            seqs_from_log = unique_seqs(seqs_from_log)
            if seqs_from_log:
                print(f"[INFO] Found {len(seqs_from_log)} unique seq(s) in log for N={N}:")
                for s in seqs_from_log:
                    print(f"  - {s}")
        except FileNotFoundError:
            print(f"[WARN] Log file not found: {args.log}")

    # 3) Probe via tiling_probe.py with exact bytes (preferred for validation)
    seq_from_probe: List[Tuple[int,int,str]] = []
    try:
        seq_from_probe = run_tiling_probe(N, last_hex, args.tiling_probe_cmd)
        if seq_from_probe:
            print(f"[INFO] tiling_probe suggests/validates seq for N={N}: {seq_from_probe}")
        else:
            print("[WARN] Could not parse a seq from tiling_probe output. "
                  "Consider checking tiling_probe output manually or capturing a DP trace.")
    except FileNotFoundError:
        print("[WARN] tiling_probe.py not found on PATH; skipping probe step.")

    # 4) Choose a candidate to emit (if any)
    candidate_seq: Optional[List[Tuple[int,int,str]]] = None
    if seq_from_probe:
        candidate_seq = seq_from_probe
    elif seqs_from_log:
        candidate_seq = seqs_from_log[0]  # pick first as a hint
    else:
        candidate_seq = None

    # 5) Print JSON snippet (and optionally write to file)
    if candidate_seq:
        snippet: Dict[str, Any] = {str(N): [[L, B, pos] for (L, B, pos) in candidate_seq]}
        snippet_json = json.dumps(snippet, indent=2)
        print("\n=== JSON snippet you could add to canonical_overrides.json ===")
        print(snippet_json)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(snippet_json + "\n")
            print(f"[INFO] Wrote snippet to {args.out}")
    else:
        print("\n[NOTE] No candidate seq was produced. You can still use N and last-N hex above to:")
        print("  - Manually run: python tiling_probe.py N --with-bytes <hex>")
        print("  - Or capture a DP trace from a mismatch run and parse 'seq' for N.")

if __name__ == "__main__":
    import sys
    main()
