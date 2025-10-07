import argparse
import json
import os
from typing import List, Tuple, Dict, Any
from main import strict_decode_serial
import csv
import pathlib
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Akamoden
# ---------- helpers ----------


def _map_bytes_to_chars(serial: str, data: bytes, used_blocks, alphabet):
    """
    Show which bytes map to which base85 characters in the serial body.
    """
    body = serial[4:]  # strip prefix (@UgX)
    mappings = []
    pos = 0
    cursor = 0
    for (L, B, pos_tag) in used_blocks:
        chunk = data[cursor:cursor+B]
        # encode this chunk alone
        from main import bit_pack_encode
        seg = bit_pack_encode(chunk, alphabet=alphabet, blocks=[(L,B)])
        mappings.append({
            "bytes": f"{cursor}..{cursor+B-1}",
            "chars": body[pos:pos+L],
            "pos": pos_tag,
            "L": L,
            "B": B
        })
        cursor += B
        pos += L
    return mappings





def _bits_from_bytes(data: bytes) -> str:
    return "".join(f"{b:08b}" for b in data)

def compare_serials(serial_a: str, serial_b: str, *,
                    log_path="serial_diff_log.csv",
                    field_map_path="field_map.json"):
    """
    Compare two serials at the raw byte level.
    Prints differences and logs them to CSV.
    Uses field_map.json if available (map byte index -> field name).
    """
    from main import strict_decode_serial

    data_a, _, _, _ = strict_decode_serial(serial_a)
    data_b, _, _, _ = strict_decode_serial(serial_b)

    print("\n[COMPARE SERIALS]")
    print(f"Serial A len={len(data_a)}")
    print(f"Serial B len={len(data_b)}")

    # optional byte-index -> field name map
    field_map = {}
    import pathlib, json
    p = pathlib.Path(field_map_path)
    if p.exists():
        try:
            field_map = json.load(p.open("r", encoding="utf-8"))
        except Exception as e:
            print(f"[WARN] Failed to load field_map.json: {e}")

    # print and collect diffs
    diffs = []
    max_len = max(len(data_a), len(data_b))
    for i in range(max_len):
        va = data_a[i] if i < len(data_a) else None
        vb = data_b[i] if i < len(data_b) else None
        if va != vb:
            label = field_map.get(str(i), "")
            label = f" ({label})" if label else ""
            va_s = f"{va}" if va is not None else "---"
            vb_s = f"{vb}" if vb is not None else "---"
            print(f"  Byte[{i}] {va_s} → {vb_s}{label}")
            diffs.append((i, va if va is not None else "", vb if vb is not None else "", label.strip(" ()")))

    # log to CSV (append)
    if diffs:
        import csv
        log_file = pathlib.Path(log_path)
        write_header = not log_file.exists()
        with log_file.open("a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if write_header:
                w.writerow(["serial_a_head", "serial_b_head", "len_a", "len_b", "byte_index", "val_a", "val_b", "field"])
            for idx, va, vb, field in diffs:
                w.writerow([serial_a[:12], serial_b[:12], len(data_a), len(data_b), idx, va, vb, field])
        print(f"[LOG] {len(diffs)} diffs recorded in {log_file}")
    else:
        print("No differences.")



def _build_block_ranges(used_blocks: List[Tuple[int, int, str]]) -> List[Dict[str, int]]:
    """
    used_blocks: [(L, B, 'mid'|'tail'), ...] from strict_decode_serial()
    Returns: [{"idx":i,"L":L,"B":B,"start":start,"end":end,"bytes":B}, ...]
    """
    ranges = []
    cursor = 0
    for i, (L, B, _pos) in enumerate(used_blocks):
        start = cursor
        end = start + B
        ranges.append({"idx": i, "L": L, "B": B, "start": start, "end": end, "bytes": B})
        cursor = end
    return ranges

def _infer_boundaries_from_positions(used_blocks, block_ranges):
    """
    Compute boundaries from 'mid'/'tail' tags returned by strict_decode_serial.
    - prefix_end: None (unknown for now)
    - mid_end   : end of the LAST block tagged 'mid', else None
    - tail_start: same as mid_end
    """
    last_mid_idx = None
    for i, (_L, _B, pos) in enumerate(used_blocks):
        if pos == "mid":
            last_mid_idx = i
    if last_mid_idx is None:
        return {"prefix_end": None, "mid_end": None, "tail_start": None}
    mid_end = block_ranges[last_mid_idx]["end"]
    return {"prefix_end": None, "mid_end": mid_end, "tail_start": mid_end}

def _emit_inspect_json(out_path: str, *, serial: str, data: bytes,
                       used_blocks, block_ranges, boundaries) -> Dict[str, Any]:
    payload = {
        "serial": serial,
        "bytes_hex": data.hex(),
        "length": len(data),
        "blocks": [{"L": L, "B": B, "pos": pos} for (L, B, pos) in used_blocks],
        "block_ranges": block_ranges,
        "boundaries": boundaries
    }
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return payload

# ---------- CLI actions ----------
def cmd_inspect(serial: str, out_path: str | None, set_mid_block: int | None):
    # 1) strict decode
    data, used_blocks, prefix, item_type = strict_decode_serial(serial)

    # 2) block table
    block_ranges = _build_block_ranges(used_blocks)

    # 3) boundaries (auto from mid/tail tags)
    boundaries = _infer_boundaries_from_positions(used_blocks, block_ranges)

    # 4) optional override: --set-mid-block INDEX → boundaries.mid_end = end of that block
    if set_mid_block is not None:
        if 0 <= set_mid_block < len(block_ranges):
            mid_end = block_ranges[set_mid_block]["end"]
            boundaries["mid_end"] = mid_end
            boundaries["tail_start"] = mid_end
            print(f"[inspect] mid block set to index {set_mid_block} → mid_end={mid_end} tail_start={mid_end}")
        else:
            print(f"[inspect] --set-mid-block {set_mid_block} out of range (0..{len(block_ranges)-1})")

    # 5) friendly print
    print(f"[inspect] prefix={prefix!r}  item_type={item_type!r}")
    print("Blocks:")
    for br in block_ranges:
        print(f"  idx {br['idx']:02d}  bytes {br['bytes']:>3}  start {br['start']:>4}  end {br['end']:>4}  (L={br['L']} B={br['B']})")
    print(f"Total raw bytes: {len(data)}")
    print(f"Boundaries: {boundaries}")

    from main import BL4_ALPHABET
    mappings = _map_bytes_to_chars(serial, data, used_blocks, BL4_ALPHABET)
    print("Byte→Char map:")
    for m in mappings:
        print(f"  {m['pos']:>4} block (L={m['L']} B={m['B']}) "
              f"bytes[{m['bytes']}] → '{m['chars']}'")

    # 6) JSON emit
    out_file = out_path if out_path else (f"{serial[:12].replace('@','at')}_inspect.json")
    _emit_inspect_json(out_file, serial=serial, data=data,
                       used_blocks=used_blocks, block_ranges=block_ranges,
                       boundaries=boundaries)
    print(f"[inspect] wrote {out_file}")

def cmd_bitdump(serial: str, limit: int):
    data, used_blocks, prefix, item_type = strict_decode_serial(serial)
    bits = _bits_from_bytes(data)
    print(f"[BITSTREAM] len={len(bits)} bits")
    print(bits[:limit] + ("..." if len(bits) > limit else ""))

def main():
    ap = argparse.ArgumentParser(description="BL4 serial inspector (boundaries + JSON export)")
    ap.add_argument("--inspect", metavar="SERIAL", help="Inspect a serial and emit JSON with blocks and boundaries.")
    ap.add_argument("--out-inspect", metavar="PATH", default=None, help="Override output JSON path for --inspect.")
    ap.add_argument("--set-mid-block", type=int, default=None, help="Mark block INDEX as last 'mid' (tail starts after).")
    ap.add_argument("--bitdump", metavar="SERIAL", help="Dump raw bitstream (debug).")
    ap.add_argument("--bitdump-limit", type=int, default=256, help="Max bits to print in --bitdump (default 256).")
    ap.add_argument("--compare-serials", nargs=2, metavar=("SERIAL_A", "SERIAL_B"),
                    help="Compare two serials and show differing bytes")

    args = ap.parse_args()

    if args.inspect:
        cmd_inspect(args.inspect, args.out_inspect, args.set_mid_block)
        return
    if args.bitdump:
        cmd_bitdump(args.bitdump, args.bitdump_limit)
        return
    if args.compare_serials:
        compare_serials(args.compare_serials[0], args.compare_serials[1])
        return

    ap.print_help()


if __name__ == "__main__":
    main()
