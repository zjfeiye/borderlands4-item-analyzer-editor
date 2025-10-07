import argparse, csv, json, pathlib, sys
from typing import List, Tuple, Dict, Optional
from types import SimpleNamespace
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Akamoden
from main import strict_decode_serial, true_encode, encode_item_serial, load_true_spec
try:
    from main import bit_pack_encode
except Exception:
    bit_pack_encode = None  # hybrid disabled if missing

def parse_inline_patch(spec: str) -> List[Tuple[int, int]]:
    if not spec:
        return []
    out: List[Tuple[int,int]] = []
    parts = [p.strip() for p in spec.split(",") if p.strip()]
    for p in parts:
        if "=" in p:
            k,v = p.split("=",1)
        elif ":" in p:
            k,v = p.split(":",1)
        else:
            raise ValueError(f"Bad patch token '{p}'. Use idx=val or idx:val.")
        def to_int(x: str) -> int:
            x = x.strip()
            return int(x, 16) if x.lower().startswith("0x") else int(x, 10)
        idx = to_int(k)
        val = to_int(v)
        if not (0 <= val <= 255):
            raise ValueError(f"Value out of range at '{p}' (0..255)")
        out.append((idx, val))
    return out

def read_csv_patches(path: str) -> List[Tuple[int,int]]:
    rows: List[Tuple[int,int]] = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            if "idx" in row and "val" in row:
                rows.append((int(row["idx"],0), int(row["val"],0)))
            elif "byte_index" in row and "new_value" in row:
                rows.append((int(row["byte_index"],0), int(row["new_value"],0)))
            else:
                keys = list(row.keys())
                if len(keys) >= 2:
                    rows.append((int(keys and row[keys[0]] or "0",0), int(keys and row[keys[1]] or "0",0)))
                else:
                    raise ValueError("CSV must have columns (idx,val) or (byte_index,new_value)")
    return rows

def read_json_patches(path: str) -> List[Tuple[int,int]]:
    obj = json.load(open(path, "r", encoding="utf-8"))
    out: List[Tuple[int,int]] = []
    if isinstance(obj, dict):
        for k,v in obj.items():
            out.append((int(k,0), int(v,0)))
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (list,tuple)) and len(item)==2:
                out.append((int(item[0],0) if isinstance(item[0],str) else int(item[0]),
                            int(item[1],0) if isinstance(item[1],str) else int(item[1])))
            else:
                raise ValueError("JSON list must be pairs [idx, val]")
    else:
        raise ValueError("JSON must be an object or list of pairs")
    return out

def hybrid_encode_mid_strict_tail_true(data: bytes, used_blocks, prefix: str, prefs: dict) -> str:
    if bit_pack_encode is None:
        raise RuntimeError("Hybrid mode unavailable: main.bit_pack_encode not found")
    tail_start = sum(B for (L,B,pos) in used_blocks if pos == "mid")
    mid_bytes = data[:tail_start]
    tail_bytes = data[tail_start:]
    mid_blocks = [(L,B) for (L,B,pos) in used_blocks if pos == "mid"]
    mid_str = bit_pack_encode(mid_bytes, blocks=mid_blocks)
    tail_str = true_encode(tail_bytes, item_type="", prefix="", prefs=prefs, debug_collect=[])
    return prefix + mid_str + tail_str

def apply_patches(serial: str, edits: List[Tuple[int,int]], *, encode_mode: str, allow_mid: bool,
                  out_file: Optional[str]=None, log_csv: Optional[str]=None):
    data, used_blocks, prefix, item_type = strict_decode_serial(serial)
    b = bytearray(data)

    tail_start = sum(B for (L,B,pos) in used_blocks if pos == "mid")
    for (idx,_) in edits:
        if not (0 <= idx < len(b)):
            raise IndexError(f"byte index {idx} out of range (len={len(b)})")
        if idx < tail_start and encode_mode != "strict" and not allow_mid:
            raise ValueError(f"edit {idx} falls in MID (0..{tail_start-1}); use --allow-mid or --encode-mode strict")

    changes = []
    for (idx,val) in edits:
        old = b[idx]
        if old != val:
            b[idx] = val
            changes.append((idx, old, val))

    _, prefs = load_true_spec()
    if encode_mode == "true":
        new_serial = true_encode(bytes(b), item_type="", prefix=prefix, prefs=prefs, debug_collect=[])
    elif encode_mode == "hybrid":
        new_serial = hybrid_encode_mid_strict_tail_true(bytes(b), used_blocks=used_blocks, prefix=prefix, prefs=prefs)
    elif encode_mode == "strict":
        strict_blocks = [(L,B) for (L,B,pos) in used_blocks]
        decoded_stub = SimpleNamespace(item_type=item_type or "", prefix=prefix or "")
        new_serial = encode_item_serial(
            decoded_item=decoded_stub,
            data=bytes(b),
            item_type=item_type,  # fine to keep; strict uses decoded_item
            prefix=prefix,
            blocks=strict_blocks
        )

    else:
        raise ValueError("encode_mode must be one of: true, hybrid, strict")

    print("\n[PATCH RESULT]")
    print(f" original len={len(data)}  tail_start={tail_start}")
    print(f" changes applied: {len(changes)}")
    for (idx, old, val) in changes:
        print(f"  byte[{idx}] {old} -> {val}")
    print("\nNEW SERIAL:\n" + new_serial)

    if log_csv and changes:
        p = pathlib.Path(log_csv)
        write_header = not p.exists()
        with p.open("a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if write_header:
                w.writerow(["serial_head", "len", "tail_start", "idx", "old", "new", "encode_mode", "new_serial_head"])
            for (idx, old, val) in changes:
                w.writerow([serial[:12], len(data), tail_start, idx, old, val, encode_mode, new_serial[:12]])
        print(f"[LOG] wrote {len(changes)} changes -> {p}")

    if out_file:
        pathlib.Path(out_file).write_text(new_serial, encoding="utf-8")
        print(f"[OUT] wrote new serial to {out_file}")
    return new_serial

def derive_patch(serial_a: str, serial_b: str) -> List[Tuple[int,int]]:
    a, _, _, _ = strict_decode_serial(serial_a)
    b, _, _, _ = strict_decode_serial(serial_b)
    n = min(len(a), len(b))
    diffs: List[Tuple[int,int]] = []
    for i in range(n):
        if a[i] != b[i]:
            diffs.append((i, b[i]))
    if len(a) != len(b):
        print(f"[WARN] length differs (A={len(a)} vs B={len(b)}); derived patch covers first {n} bytes only")
    return diffs

def read_serial_arg(serial: Optional[str], serial_file: Optional[str]) -> str:
    if serial_file:
        return pathlib.Path(serial_file).read_text(encoding="utf-8", errors="ignore").strip()
    if serial:
        return serial
    raise ValueError("Provide --serial or --serial-file")

def main():
    ap = argparse.ArgumentParser(description="Multi-byte patcher with full TRUE re-encode")
    g_in = ap.add_argument_group("input")
    g_in.add_argument("--serial", help="Input serial (quote carefully in PowerShell)")
    g_in.add_argument("--serial-file", help="Read serial from a file (safer for PS quoting)")

    g_patch = ap.add_argument_group("patch sources")
    g_patch.add_argument("--patch", help="Inline patch spec: idx=val,idx=val (idx/val allow hex 0x..)")
    g_patch.add_argument("--patch-csv", help="CSV with columns (idx,val) or (byte_index,new_value)")
    g_patch.add_argument("--patch-json", help="JSON mapping {idx: val} or list [[idx,val],...]")

    g_mode = ap.add_argument_group("mode / safety")
    g_mode.add_argument("--encode-mode", choices=["true","hybrid","strict"], default="true",
                        help="Re-encode strategy (default: true)")
    g_mode.add_argument("--allow-mid", action="store_true", help="Allow edits in MID region (dangerous unless encode-mode=strict)")

    g_out = ap.add_argument_group("output")
    g_out.add_argument("--out-file", help="Write new serial to this file")
    g_out.add_argument("--log-csv", help="Append a change log CSV")

    g_der = ap.add_argument_group("derive patch from another serial")
    g_der.add_argument("--derive-patch", nargs=2, metavar=("SERIAL_A","SERIAL_B"),
                       help="Compute patch that transforms A's bytes into B's (uses strict decode).")
    g_der.add_argument("--derive-patch-file", nargs=2, metavar=("FILE_A","FILE_B"),
                       help="Same as --derive-patch but read both from files.")
    g_der.add_argument("--print-patch", action="store_true", help="Print derived patch as inline 'idx=val' list.")
    g_der.add_argument("--apply-derived", action="store_true", help="After deriving from A->B, apply patch to A and emit new serial.")

    args = ap.parse_args()

    # Derive-only flow
    if args.derive_patch or args.derive_patch_file:
        if args.derive_patch_file:
            a = pathlib.Path(args.derive_patch_file[0]).read_text(encoding="utf-8", errors="ignore").strip()
            b = pathlib.Path(args.derive_patch_file[1]).read_text(encoding="utf-8", errors="ignore").strip()
        else:
            a, b = args.derive_patch
        diffs = derive_patch(a, b)
        if args.print_patch:
            spec = ",".join([f"{i}={v}" for (i,v) in diffs])
            print(spec)
        else:
            for (i,v) in diffs:
                print(f"{i}={v}")
        if args.apply_derived:
            apply_patches(a, diffs, encode_mode=args.encode_mode, allow_mid=args.allow_mid,
                          out_file=args.out_file, log_csv=args.log_csv)
        return

    # Normal patch flow
    serial = read_serial_arg(args.serial, args.serial_file)

    edits: List[Tuple[int,int]] = []
    if args.patch:
        edits += parse_inline_patch(args.patch)
    if args.patch_csv:
        edits += read_csv_patches(args.patch_csv)
    if args.patch_json:
        edits += read_json_patches(args.patch_json)

    # Deduplicate keeping last occurrence
    last_for_idx: Dict[int,int] = {}
    for (i,v) in edits:
        last_for_idx[i] = v
    edits = sorted([(i,v) for (i,v) in last_for_idx.items()], key=lambda x: x[0])

    if not edits:
        print("[ERROR] no edits provided. Use --patch/--patch-csv/--patch-json or --derive-patch*")
        sys.exit(2)

    apply_patches(serial, edits, encode_mode=args.encode_mode, allow_mid=args.allow_mid,
                  out_file=args.out_file, log_csv=args.log_csv)

if __name__ == "__main__":
    main()