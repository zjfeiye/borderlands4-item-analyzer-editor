# SPDX-License-Identifier: MIT
#!/usr/bin/env python3
"""
batch_byte_inspect.py
Batch-inspect one or more BL4 serials and write a CSV table per serial or a combined CSV.

Usage examples:
  python batch_byte_inspect.py --serial "@Ug..." --out combined.csv
  python batch_byte_inspect.py --serial-file serials.txt --out combined.csv --fmt both
  python batch_byte_inspect.py --csv-in serials.csv --csv-col serial --out combined.csv

Notes:
  - Uses strict decode to recover bytes and zone (mid/tail).
  - Output columns: serial_head, index, dec, hex, chr, zone
"""
import argparse, csv, sys
from typing import Iterable, List
from main import strict_decode_serial

def iter_serials(args) -> Iterable[str]:
    if args.serial:
        for s in args.serial:
            yield s.strip()
    if args.serial_file:
        with open(args.serial_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                s = line.strip()
                if s:
                    yield s
    if args.csv_in and args.csv_col:
        import csv
        with open(args.csv_in, "r", encoding="utf-8", newline="") as f:
            r = csv.DictReader(f)
            for row in r:
                s = (row.get(args.csv_col) or "").strip()
                if s:
                    yield s

def fmt_ascii(v: int) -> str:
    return chr(v) if 32 <= v <= 126 else "."

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--serial", action="append", help="Serial string (repeatable)")
    ap.add_argument("--serial-file", help="Text file of serials (one per line)")
    ap.add_argument("--csv-in", help="CSV file containing serials")
    ap.add_argument("--csv-col", help="Column name in --csv-in that holds the serial text")
    ap.add_argument("--out", default="byte_inspect.csv", help="Output CSV path (combined)")
    ap.add_argument("--fmt", choices=["dec","hex","both"], default="both", help="Display format (affects dec/hex strings)")
    args = ap.parse_args()

    if not (args.serial or args.serial_file or (args.csv_in and args.csv_col)):
        ap.error("Provide --serial (repeatable), or --serial-file, or --csv-in with --csv-col.")

    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["serial_head", "index", "dec", "hex", "chr", "zone"])

        count = 0
        for s in iter_serials(args):
            try:
                data, used_blocks, prefix, item_type = strict_decode_serial(s)
            except Exception as e:
                print(f"[DECODE_FAIL] {s[:40]}... :: {e}", file=sys.stderr)
                continue

            # Build zone map
            total = sum(B for (_,B,_) in used_blocks)
            zones = [None] * total
            off = 0
            for (L,B,pos) in used_blocks:
                for i in range(off, off+B):
                    zones[i] = pos
                off += B

            head = s[:12]
            for i, b in enumerate(data):
                if args.fmt == "dec":
                    dec, hx = str(b), ""
                elif args.fmt == "hex":
                    dec, hx = "", f"0x{b:02X}"
                else:
                    dec, hx = str(b), f"0x{b:02X}"
                w.writerow([head, i, dec, hx, fmt_ascii(b), zones[i]])
            count += 1

    print(f"[OK] Wrote {args.out} for {count} serial(s).")

if __name__ == "__main__":
    main()
