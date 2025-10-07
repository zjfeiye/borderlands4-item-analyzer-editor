import os
import sys
from collections import defaultdict, Counter
import json
from types import SimpleNamespace
from main import (
    BL4_ALPHABET,
    bit_pack_decode,
    bit_pack_encode,
    encode_item_serial,
    TRUE_BLOCKS_BASELINE,
    true_encode,
    strict_decode_serial,
    load_true_spec,
)


LOG_PATH_DEFAULT = os.environ.get("BL4_EDIT_LOG", "edit_log.csv")

# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Akamoden

# ========= Byte dump helpers =========

def _byte_zone_lookup(used_blocks):
    """Return a list the size of total bytes mapping each index -> 'mid' or 'tail'."""
    total = sum(B for (_, B, _) in used_blocks)
    zones = [None] * total
    off = 0
    for (L, B, pos) in used_blocks:
        for i in range(off, off + B):
            zones[i] = pos
        off += B
    return zones

def _fmt_val(v: int | None, fmt: str):
    if v is None:
        return ("---", "---", "·")
    dec = f"{v:3d}"
    hx  = f"0x{v:02X}"
    asc = chr(v) if 32 <= v <= 126 else "·"
    if fmt == "hex":
        return (hx, None, asc)
    if fmt == "dec":
        return (dec, None, asc)
    # both
    return (dec, hx, asc)

def dump_serial_bytes(serial: str, *, fmt: str = "both", start: int | None = None,
                      end: int | None = None, show_ascii: bool = True):
    """
    Strict-decode one serial and list every byte line-by-line with index,
    decimal/hex, ASCII (printable), and whether it's in a mid or tail block.
    """
    from main import strict_decode_serial
    data, used_blocks, prefix, item_type = strict_decode_serial(serial)
    zones = _byte_zone_lookup(used_blocks)

    n = len(data)
    s = 0 if start is None else max(0, start)
    e = n if end is None else min(n, end)

    print(f"\n[INSPECT BYTES] len={n}  prefix={prefix!r} type={item_type!r}")
    print(" index  dec   hex   chr  zone")
    print(" -----  ----- ----- ---  ----")
    for i in range(s, e):
        dec, hx, asc = _fmt_val(data[i], fmt)
        if fmt == "dec":
            cols = f"{dec:>5}"
        elif fmt == "hex":
            cols = f"{hx:>5}"
        else:
            cols = f"{dec:>5} {hx:>5}"
        cols_chr = f" {asc:>3}" if show_ascii else ""
        print(f" {i:5d}  {cols}{cols_chr}  {zones[i]}")







def hybrid_encode_mid_strict_tail_true(
    data: bytes | bytearray,
    used_blocks,         # [(L,B,'mid'|'tail'), ...] from strict_decode_serial
    prefix: str,
    item_type: str,
    prefs: dict,
):
    """
    Keep the mid section exactly as strict-encoded with the original blocks;
    re-encode only the tail with TRUE DP so edits can breathe.
    """
    from main import bit_pack_encode, true_encode

    data = bytes(data)

    # mid/tail split (based on strict decode)
    tail_start = sum(B for (L, B, pos) in used_blocks if pos == "mid")
    mid_bytes  = data[:tail_start]
    tail_bytes = data[tail_start:]

    # strict-encode mid exactly as original tiling
    mid_blocks = [(L, B) for (L, B, pos) in used_blocks if pos == "mid"]
    mid_str = bit_pack_encode(mid_bytes, blocks=mid_blocks)

    # TRUE-encode tail only; pass prefix="" so we get just the body for the tail
    trace = []
    tail_str = true_encode(tail_bytes, item_type="", prefix="", prefs=prefs, debug_collect=trace)

    return prefix + mid_str + tail_str


# --- Add this lightweight byte-level comparator (optionally CSV) ---
def compare_bytes(serial_a: str, serial_b: str, csv_path: str | None = None,
                  show_blocks: bool = True, show_all: bool = False, fmt: str = "both"):
    """
    Decode two serials and print a byte-by-byte table.
    If show_all=True, prints every index (marking '=' for matches).
    """
    from main import strict_decode_serial

    a_bytes, a_blocks, a_prefix, a_type = strict_decode_serial(serial_a)
    b_bytes, b_blocks, b_prefix, b_type = strict_decode_serial(serial_b)

    print("\n[COMPARE]")
    print(f" A len={len(a_bytes)}  prefix={a_prefix!r} type={a_type!r}")
    print(f" B len={len(b_bytes)}  prefix={b_prefix!r} type={b_type!r}")
    if show_blocks:
        print(" A blocks:", a_blocks)
        print(" B blocks:", b_blocks)

    max_len = max(len(a_bytes), len(b_bytes))
    print("\n idx   A(dec/hex)  B(dec/hex)  chrA chrB  mark")
    print(" ----  -----------  -----------  ---- ----  ----")
    diffs = []
    for i in range(max_len):
        va = a_bytes[i] if i < len(a_bytes) else None
        vb = b_bytes[i] if i < len(b_bytes) else None
        a_dec, a_hex, a_asc = _fmt_val(va, fmt)
        b_dec, b_hex, b_asc = _fmt_val(vb, fmt)

        if fmt == "dec":
            a_show = f"{a_dec:>3}"
            b_show = f"{b_dec:>3}"
        elif fmt == "hex":
            a_show = f"{a_hex:>4}"
            b_show = f"{b_hex:>4}"
        else:
            a_show = f"{a_dec:>3}/{a_hex[-2:] if a_hex!='---' else '--'}"
            b_show = f"{b_dec:>3}/{b_hex[-2:] if b_hex!='---' else '--'}"

        mark = "!=" if va != vb else "="
        if va != vb or show_all:
            print(f" {i:4d}  {a_show:>11}  {b_show:>11}   {a_asc:>3}  {b_asc:>3}   {mark}")
        if va != vb:
            diffs.append((i, va if va is not None else "", vb if vb is not None else ""))

    if csv_path and diffs:
        import csv, pathlib
        p = pathlib.Path(csv_path)
        write_header = not p.exists()
        with p.open("a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if write_header:
                w.writerow(["serial_a_head", "serial_b_head", "idx", "val_a", "val_b",
                            "len_a", "len_b"])
            for idx, va, vb in diffs:
                w.writerow([serial_a[:12], serial_b[:12], idx, va, vb, len(a_bytes), len(b_bytes)])
        print(f"[LOG] {len(diffs)} diffs → {csv_path}")
    elif not diffs:
        print("  No byte differences.")



# === TRUE re-encode helpers ================================================

def true_encode_full(data: bytes | bytearray, *, prefix: str, prefs: dict) -> str:
    """
    Re-encode the entire payload via TRUE (canonicals first, then DP),
    preserving the original serial's prefix.
    """
    from main import true_encode
    trace = []
    return true_encode(bytes(data), item_type="", prefix=prefix, prefs=prefs, debug_collect=trace)

def reencode_after_edit(
    data: bytes | bytearray,
    *,
    used_blocks,            # from strict_decode_serial
    prefix: str,
    item_type: str,
    prefs: dict,
    encode_mode: str = "true",  # "true" | "hybrid" | "strict"
) -> str:
    """
    Choose how to rebuild the serial after edits:
      - true    : full TRUE re-encode (preferred)
      - hybrid  : strict mid, TRUE tail
      - strict  : full strict (original tiling)
    """
    from main import encode_item_serial

    if encode_mode == "true":
        return true_encode_full(data, prefix=prefix, prefs=prefs)

    if encode_mode == "hybrid":
        # keep mids exactly; re-encode only the tail
        return hybrid_encode_mid_strict_tail_true(
            data, used_blocks=used_blocks, prefix=prefix, item_type=item_type, prefs=prefs
        )

    # strict (same tiling)
    strict_blocks = [(L, B) for (L, B, pos) in used_blocks]
    decoded_stub = SimpleNamespace(item_type=item_type or "", prefix=prefix or "")
    return encode_item_serial(
        decoded_item=decoded_stub,
        data=bytes(data),
        item_type=item_type,
        prefix=prefix,
        blocks=strict_blocks
    )









# ---------- Utility printing ----------
import pathlib
def hybrid_encode(data: bytes, item_type: str, prefix: str, used_blocks, prefs):
    """
    Try strict encode first with exact tiling.
    If it fails (e.g. after byte edits), fall back to true_encode.
    """
    from main import encode_item_serial, true_encode

    class _Stub:
        def __init__(self, t): self.item_type = t

    # Try strict with decode tiling
    try:
        blocks = [(L, B) for (L, B, pos) in used_blocks]
        return encode_item_serial(_Stub(item_type), data, blocks=blocks)
    except Exception as e:
        print(f"[HYBRID] Strict failed, falling back to true_encode: {e}")
        trace = []
        return true_encode(data, item_type="", prefix=prefix, prefs=prefs, debug_collect=trace)



def inspect_serial(target_head: str):
    """
    Find the first serial in corpus.txt starting with target_head,
    print its raw length, and compare strict vs true encoders.
    """
    from main import strict_decode_serial, encode_item_serial, true_encode, load_true_spec

    # 1) Load corpus
    with open("corpus.txt", "r", encoding="utf-8") as f:
        serials = [line.strip() for line in f if line.strip()]

    # 2) Find matching serial
    serial = next((s for s in serials if s.startswith(target_head)), None)
    if not serial:
        print(f"[ERROR] No serial found starting with {target_head}")
        return

    print(f"\n[INSPECT] Serial head={target_head}")
    print(f"Original serial length (incl. prefix): {len(serial)}")
    print(f"Original serial: {serial}")

    # 3) Decode strict
    data, used_blocks, prefix, item_type = strict_decode_serial(serial)
    print(f"Strict decode blocks: {used_blocks}")

    # 4) Strict re-encode with exact tiling
    class _Stub:
        def __init__(self, t): self.item_type = t
    blocks = [(L, B) for (L, B, pos) in used_blocks]
    strict_out = encode_item_serial(_Stub(item_type), data, blocks=blocks)

    # 5) True re-encode
    _, prefs = load_true_spec()
    trace = []
    true_out = true_encode(data, item_type="", prefix=prefix, prefs=prefs, debug_collect=trace)
    out = hybrid_encode(data, item_type, prefix, used_blocks, prefs)

    # 6) Print results
    print(f"\nStrict out (len={len(strict_out)}): {strict_out}")
    print(f"True   out (len={len(true_out)}): {true_out}")

    if strict_out != serial:
        print("⚠️ Strict re-encode does not match original corpus!")
    if true_out != serial:
        print("⚠️ True re-encode does not match original corpus!")

    # 7) Diff
    if strict_out != true_out:
        print("\n--- Char-by-char diff ---")
        for i, (a, b) in enumerate(zip(strict_out, true_out)):
            marker = " " if a == b else "!"
            print(f"{i:03d}: {a} {b} {marker}")
        if len(strict_out) != len(true_out):
            print(f"[LEN] strict={len(strict_out)} true={len(true_out)}")

    print("\n--- True trace ---")
    for step in trace:
        print(step)
    print("--- end trace ---")

def test_edit_mode(serial: str, byte_index: int, new_value: int):
    """
    Load a serial, flip one raw byte, and try encoding with strict vs true.
    """
    from main import strict_decode_serial, encode_item_serial, true_encode, load_true_spec

    print(f"\n[EDIT MODE TEST] Serial head={serial[:30]}...")

    # Step 1: strict decode
    data, used_blocks, prefix, item_type = strict_decode_serial(serial)
    print(f"Original length={len(serial)}, strict blocks={used_blocks}")

    # Step 2: modify raw bytes
    data_mut = bytearray(data)
    if byte_index < len(data_mut):
        old_val = data_mut[byte_index]
        data_mut[byte_index] = new_value
        print(f"Changed byte[{byte_index}] {old_val} → {new_value}")
    else:
        print(f"[ERROR] byte_index {byte_index} out of range (len={len(data_mut)})")
        return

    # Step 3: strict re-encode
    class _Stub:
        def __init__(self, t): self.item_type = t
    blocks = [(L, B) for (L, B, pos) in used_blocks]
    try:
        strict_out = encode_item_serial(_Stub(item_type), bytes(data_mut), blocks=blocks)
        print(f"Strict out (len={len(strict_out)}): {strict_out}")
    except Exception as e:
        print(f"⚠️ Strict encode failed: {e}")
        strict_out = None

    # Step 4: true re-encode
    _, prefs = load_true_spec()
    trace = []
    try:
        true_out = true_encode(bytes(data_mut), item_type="", prefix=prefix, prefs=prefs, debug_collect=trace)
        print(f"True out   (len={len(true_out)}): {true_out}")
    except Exception as e:
        print(f"True encode failed: {e}")
        true_out = None

    # Step 5: if strict failed but true worked, show trace
    if strict_out is None and true_out is not None:
        print("\n--- True decision trace ---")
        for step in trace[:50]:
            print(step)
        print("--- end trace ---")



def print_true_capacity_stats(block_stats, quarantined_stats):
    print("\n========== Per-block TRUE capacity stats ==========")
    for (L, B), st in block_stats.items():
        ok = st["ok"]
        total = st["total"]
        status = "OK" if ok == total else f"FAIL ({total-ok})"
        mx85 = st.get("max85", 0)
        mxv  = st.get("max_v85_seen", 0)
        mxb  = st.get("max_byte_val", 0)
        print(f" {L}→{B: <2} | {ok}/{total} ok ({ok/total*100:.1f}%) | {status: <10} | max85={mx85}b  max_v85_seen={mxv}b  max_byte_val={mxb}b")
        if st.get("needed"):
            for nb, cnt in st["needed"].items():
                print(f"    needed {nb} bytes: {cnt} times ({cnt/total*100:.1f}%)")
        if st.get("examples"):
            for ex in st["examples"][:5]:
                print(f"    eg: {ex}")

    print("\n========== Quarantined blocks (skipped in search) ==========")
    for (L, B), st in quarantined_stats.items():
        total = st["total"]
        print(f" {L}→{B: <2} | 0/{total} ok (0.0%) | QUARANTINED ({total}) | max85=0b  max_v85_seen=0b  max_byte_val=0b")
        for ex in st.get("examples", [])[:5]:
            print(f"    eg: {ex}")

def print_summary(block_stats, quarantined_stats):
    normal_ok = sum(st["ok"] for st in block_stats.values())
    normal_tot = sum(st["total"] for st in block_stats.values())
    q_tot = sum(st["total"] for st in quarantined_stats.values())
    print("\n========== Summary ==========")
    print(f"Normal blocks: {normal_ok}/{normal_tot} ok ({(normal_ok/normal_tot*100 if normal_tot else 0):.1f}%)")
    print(f"Quarantined blocks: 0/{q_tot} ok (0.0%)")
    print("===================================================\n")

# ---------- Corpus loader (your existing mechanism) ----------
def load_corpus():
    # Your project already loads the 10,057 serials internally.
    # Replace this with your actual loader if different.
    with open("corpus.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# ---------- Derive TRUE_BLOCKS + preferences from OK path ----------
def derive_true_from_ok_path(roundtrip_records):
    """
    roundtrip_records: iterable of tuples produced by your strict round-trip:
       (serial, decoded_bytes, used_blocks) where used_blocks is [(L,B,pos), ...]
    Returns:
       true_spec (dict), prefs (dict: {(B,'mid'|'tail'): [L...most_common_first]})
    """
    ok_counters = defaultdict(lambda: Counter())      # key: (B,pos) -> Counter of L
    ok_presence = defaultdict(lambda: {"mid": False, "tail": False})  # (L,B) presence by pos

    allowed_l_by_b = defaultdict(set)

    for _, _, used_blocks in roundtrip_records:
        for L, B, pos in used_blocks:
            allowed_l_by_b[B].add(L)
            ok_counters[(B, pos)][L] += 1
            if pos == "mid":
                ok_presence[(L, B)]["mid"] = True
            else:
                ok_presence[(L, B)]["tail"] = True

    # Build tail_only / mid_only sets
    tail_only = []
    mid_only = []
    for (L, B), seen in ok_presence.items():
        mid = seen["mid"]
        tail = seen["tail"]
        if tail and not mid:
            tail_only.append([L, B])
        elif mid and not tail:
            mid_only.append([L, B])

    true_spec = {
        "allowed_l_by_b": {int(B): sorted(list(Ls)) for B, Ls in sorted(allowed_l_by_b.items())},
        "tail_only": sorted(tail_only),
        "mid_only": sorted(mid_only),
    }

    # Build per-position L preference: most-common first
    prefs = {}
    for (B, pos), ctr in ok_counters.items():
        ordered = sorted(ctr.keys())  # prefer smaller encodings first
        prefs[(B, pos)] = ordered

    # --- Ensure prefs cover all allowed_l_by_b combos (after merging baseline/fallbacks) ---
    for B, Ls in true_spec["allowed_l_by_b"].items():
        for pos in ("mid", "tail"):
            if (B, pos) not in prefs or not prefs[(B, pos)]:
                # default to smallest-first ordering
                prefs[(B, pos)] = sorted(Ls)


    # --- Force canonical pref order for tricky cases ---
    # 3-byte tail blocks are valid with 2- or 4-digit encodings.
    # Canonicalize prefs so 2 is always preferred before 4.


    return true_spec, prefs

# ---------- Pretty print TRUE blocks ----------
def print_true_blocks(true_spec, ok_counters):
    print("\n========== True Blocks (OK-path only) ==========")
    # Reconstruct ok counts by (L,B)
    ok_by_LB = defaultdict(int)
    for (B,pos), ctr in ok_counters.items():
        for L, c in ctr.items():
            ok_by_LB[(L,B)] += c

    # For readability show by increasing B
    for B in sorted(true_spec["allowed_l_by_b"].keys()):
        Ls = true_spec["allowed_l_by_b"][B]
        # compute per-L ok totals
        parts = []
        for L in Ls:
            parts.append(f"{L}")
        # where?
        where_mid = any((L,B) not in true_spec["tail_only"] for L in Ls)
        where_tail = any((L,B) not in true_spec["mid_only"] for L in Ls)
        where = "mid+tail" if (where_mid and where_tail) else ("mid" if where_mid else "tail")
        print(f" {Ls[0]}→{B: <2} | ok={sum(ok_by_LB[(L,B)] for L in Ls): <5} | allowed L: {Ls} | where={where}")
    print("===============================================\n")




# ---------- Main ----------
def main():

    serials = load_corpus()


    # 1) Strict decode → strict encode (tiling) check
    # 1) Strict decode → strict encode (tiling) check
    roundtrip_records = []
    mismatches = 0
    for serial in serials:
        try:
            data, used_blocks_full, prefix, item_type = strict_decode_serial(serial)
            if serial.startswith("@Ugr%DXm/)}}!fXUhs#5El1B%r8Xe@~*00"):  # match your mismatch serial head
                print("[DEBUG strict blocks]", used_blocks_full)
        except Exception as e:
            print(f"[DECODE_FAIL] {serial[:40]}... :: {e}")
            return 2

        # Minimal stub to preserve original item_type in the strict encoder
        class _Stub:
            def __init__(self, t): self.item_type = t

        # strip pos tag for encoding
        blocks = [(L, B) for (L, B, pos) in used_blocks_full]

        reenc_strict = encode_item_serial(
            decoded_item=_Stub(item_type),
            data=data,
            blocks=blocks
        )
        if reenc_strict != serial:
            print(f"[STRICT_MISMATCH] {serial[:40]}... != {reenc_strict[:40]}...")
            mismatches += 1
            break

        # keep full triples (L,B,pos) for TRUE derivation
        roundtrip_records.append((serial, data, used_blocks_full))

    ok_count = len(roundtrip_records)
    print(f"\nStrict round-trip: {ok_count}/{len(serials)} matched ({ok_count/len(serials)*100:.1f}%)")

    if mismatches:
        return 2

    # 2) Derive TRUE spec + prefs from OK path
    true_spec, prefs = derive_true_from_ok_path(roundtrip_records)
    for B, Ls in TRUE_BLOCKS_BASELINE["allowed_l_by_b"].items():
        if B not in true_spec["allowed_l_by_b"]:
            true_spec["allowed_l_by_b"][B] = Ls
        else:
            for L in Ls:
                if L not in true_spec["allowed_l_by_b"][B]:
                    true_spec["allowed_l_by_b"][B].append(L)
                    true_spec["allowed_l_by_b"][B].sort()

    # Merge tail_only and mid_only
    true_spec["tail_only"] = sorted(list({
        tuple(x) for x in true_spec.get("tail_only", []) + TRUE_BLOCKS_BASELINE.get("tail_only", [])
    }))
    true_spec["mid_only"] = sorted(list({
        tuple(x) for x in true_spec.get("mid_only", []) + TRUE_BLOCKS_BASELINE.get("mid_only", [])
    }))

    # Ensure 3-byte tail coverage (corpus showed L=2 for B=3 at tail)
    if 3 not in true_spec["allowed_l_by_b"]:
        true_spec["allowed_l_by_b"][3] = [2, 4]
    else:
        for L in (2, 4):
            if L not in true_spec["allowed_l_by_b"][3]:
                true_spec["allowed_l_by_b"][3].append(L)
        true_spec["allowed_l_by_b"][3].sort()

    true_spec["tail_only"].append([2, 3])
    true_spec["tail_only"].append([4, 3])
    true_spec["tail_only"] = sorted(list({tuple(x) for x in true_spec["tail_only"]}))

    used_pairs = set()
    for _, _, used_blocks in roundtrip_records:
        for (L, B, pos) in used_blocks:
            used_pairs.add((L, B))

    # anything in BLOCKS but not seen in corpus → quarantine
    from main import BLOCKS, QUARANTINE_BLOCKS
    QUARANTINE_BLOCKS.clear()
    for (L, B) in BLOCKS:
        if (L, B) not in used_pairs:
            QUARANTINE_BLOCKS.add((L, B))

    print(f"[INFO] Auto-quarantined {len(QUARANTINE_BLOCKS)} unused blocks: {sorted(QUARANTINE_BLOCKS)}")
    block_counter = Counter()
    for _, _, used_blocks in roundtrip_records:
        for (L, B, pos) in used_blocks:
            block_counter[(L, B)] += 1

    print("\n[STATS] Block usage frequencies across corpus:")
    unused_blocks = []
    for (L, B) in sorted(BLOCKS, key=lambda x: (x[1], x[0])):
        count = block_counter.get((L, B), 0)
        print(f"  (L={L}, B={B}): {count}")
        if count == 0:
            unused_blocks.append((L, B))

    # --- update quarantine set + save to JSON ---
    QUARANTINE_BLOCKS.clear()
    QUARANTINE_BLOCKS.update(unused_blocks)
    print(f"[INFO] Auto-quarantined {len(QUARANTINE_BLOCKS)} unused blocks: {sorted(QUARANTINE_BLOCKS)}")

    with open("quarantine.json", "w", encoding="utf-8") as f:
        json.dump(sorted(unused_blocks), f, indent=2)

    # Overwrite canonical JSON for consistency (include prefs too)
    prefs_str = {f"{B}:{pos}": Ls for (B, pos), Ls in prefs.items()}
    with open("true_blocks.json", "w", encoding="utf-8") as f:
        json.dump({"true_spec": true_spec, "prefs": prefs_str}, f, indent=2, sort_keys=True)
    print("Exported canonical TRUE_BLOCKS (with prefs) to true_blocks.json")

    qpath = pathlib.Path("quarantine.json")
    if qpath.exists():
        try:
            with open(qpath, "r", encoding="utf-8") as fq:
                qlist = json.load(fq)
                QUARANTINE_BLOCKS.clear()
                QUARANTINE_BLOCKS.update(tuple(x) for x in qlist)
            print(f"[INFO] Loaded {len(QUARANTINE_BLOCKS)} quarantined blocks from quarantine.json")
        except Exception as e:
            print(f"[WARN] Failed to load quarantine.json: {e}")

    # Reload the canonical rules + prefs
    true_spec, prefs = load_true_spec()
    print("[DEBUG round_trip] after reload prefs for (3,'tail') =", prefs.get((3, "tail")))

    # Force canonical prefs for 3-byte tail blocks regardless of JSON
    # Force canonical prefs for 3-byte tail blocks regardless of JSON
    prefs[(3, "tail")] = [2, 3, 4]
    true_spec["allowed_l_by_b"][3] = [2, 3, 4]

    # Force 25→20 mid-preference over 24→20 mid
    prefs[(20, "mid")] = [25, 24]

    # For rem=37, prefer 25→20 mid so it pairs with 5→4 tail
    # (not 20→20 mid + 17→14 tail, which strict never uses)
    prefs[(20, "mid")] = [25, 24]  # reinforce
    prefs[(4, "tail")] = [5]  # ensure strict 5→4 tail


    # 3) Test standalone true encoder with derived prefs (hard-fail at first mismatch)
    mismatches_logged = 0
    MAX_MISMATCHES = 50  # change to 500 if you want more

    for serial, data, used_blocks in roundtrip_records:
        prefix = serial[:4]
        trace = []
        out = true_encode(data, item_type="", prefix=prefix, prefs=prefs, debug_collect=trace)
        if out != serial:
            print(f"[TRUE_MISMATCH] serial head={serial[:12]}...")

            # Strict re-encode using exact blocks
            class _Stub:
                def __init__(self, t): self.item_type = t

            blocks = [(L, B) for (L, B, pos) in used_blocks]
            strict_out = encode_item_serial(_Stub(""), data, blocks=blocks)

            print("Strict =", strict_out)
            print("True   =", out)

            # Char-by-char diff
            for i, (a, b) in enumerate(zip(strict_out, out)):
                marker = " " if a == b else "!"
                print(f"{i:03d}: {a} {b} {marker}")
            if len(strict_out) != len(out):
                print(f"[LEN] strict={len(strict_out)} true={len(out)}")

            # Decision trace
            print("\n--- True-encode decision trace ---")
            for step in trace:
                print(step)
            print("--- end trace ---\n")

            print("\n--- Debug summary ---")
            print(f"Serial head = {serial[:12]}...  raw_len={len(data)}")
            print(f"Strict used_blocks = {[(L, B) for (L, B, pos) in used_blocks]}")
            print(f"Strict total bytes = {sum(B for (L, B, pos) in used_blocks)}")
            print(f"True decision trace (first 3 steps) = {trace[:3]}")
            print("--- end summary ---\n")

            mismatches_logged += 1
            if mismatches_logged >= MAX_MISMATCHES:
                break

    # after loop: don’t return yet, let stats print
    if mismatches_logged > 0:
        print(f"[INFO] {mismatches_logged} mismatches found none")
        return 2

    print("True encoder: 100% 1:1 match on corpus ✅")
    block_counter = Counter()
    for _, _, used_blocks in roundtrip_records:
        for (L, B, pos) in used_blocks:
            block_counter[(L, B)] += 1

    print("\n[STATS] Block usage frequencies across corpus:")
    unused_blocks = []
    for (L, B) in sorted(BLOCKS, key=lambda x: (x[1], x[0])):
        count = block_counter.get((L, B), 0)
        print(f"  (L={L}, B={B}): {count}")
        if count == 0:
            unused_blocks.append((L, B))

    # --- update quarantine set + save to JSON ---
    QUARANTINE_BLOCKS.clear()
    QUARANTINE_BLOCKS.update(unused_blocks)
    print(f"[INFO] Auto-quarantined {len(QUARANTINE_BLOCKS)} unused blocks: {sorted(QUARANTINE_BLOCKS)}")

    with open("quarantine.json", "w", encoding="utf-8") as f:
        json.dump(sorted(unused_blocks), f, indent=2)
    return 0

def test_one_serial(serial: str, prefs):
    from main import strict_decode_serial, encode_item_serial, true_encode

    print("\n[TEST] Checking single serial:")
    print("  serial =", serial[:80], "...")
    import main as _m
    print("[DEBUG] using main.py:", getattr(_m, "__file__", "<unknown>"))
    print("[DEBUG] True impl tag:", getattr(_m, "TRUE_IMPL_TAG", "<unset>"))

    data, used_blocks, prefix, item_type = strict_decode_serial(serial)

    class _Stub: 
        def __init__(self, t): self.item_type = t
    blocks = [(L, B) for (L, B, pos) in used_blocks]
    strict_out = encode_item_serial(_Stub(item_type), data, blocks=blocks)

    trace = []
    err = None
    try:
        true_out = true_encode(data, item_type="", prefix=prefix, prefs=prefs, debug_collect=trace)
    except Exception as e:
        true_out = None
        err = str(e)

    print("Strict vs True:")
    print("True   =", true_out)

    if strict_out != true_out:
        if true_out is None:
            print("\n[ERROR] TRUE encoder failed:", err or "(no message)")
            if trace:
                print("\n--- True-encode decision trace ---")
                for step in trace:
                    print(step)
                print("--- end trace ---")
            return

        print("\n--- Char-by-char diff ---")
        for i, (a, b) in enumerate(zip(strict_out, true_out)):
            marker = " " if a == b else "!"
            print(f"{i:03d}: {a} {b} {marker}")
        if len(strict_out) != len(true_out):
            print(f"[LEN] strict={len(strict_out)} true={len(true_out)}")

        print("\n--- True-encode decision trace ---")
        for step in trace:
            print(step)
        print("--- end trace ---")
    else:
        print("PASS Strict and True outputs match exactly!")


def dump_bitstream(data: bytes, limit=128):
    """Dump the bitstream of decoded serial bytes."""
    bits = ''.join(f"{b:08b}" for b in data)
    print(f"[BITSTREAM] len={len(bits)} bits")
    print(bits[:limit] + ("..." if len(bits) > limit else ""))
    return bits

def test_one_serial_with_hybrid(serial: str, prefs):
    from main import strict_decode_serial, encode_item_serial, true_encode

    print("\n[HYBRID TEST] Checking single serial:")
    print("  serial =", serial[:80], "...")
    import main as _m
    print("[DEBUG] using main.py:", getattr(_m, "__file__", "<unknown>"))
    print("[DEBUG] True impl tag:", getattr(_m, "TRUE_IMPL_TAG", "<unset>"))

    # Step 1: strict decode
    data, used_blocks, prefix, item_type = strict_decode_serial(serial)

    # Step 2: strict re-encode
    class _Stub:
        def __init__(self, t): self.item_type = t
    blocks = [(L, B) for (L, B, pos) in used_blocks]
    strict_out = encode_item_serial(_Stub(item_type), data, blocks=blocks)

    # Step 3: hybrid re-encode (strict mid + true tail)
    hybrid_out = hybrid_encode_mid_strict_tail_true(
        data, used_blocks, prefix, item_type, prefs
    )

    # Step 4: true re-encode
    trace = []
    true_out = true_encode(data, item_type="", prefix=prefix, prefs=prefs, debug_collect=trace)

    # Step 5: print results
    print("Strict =", strict_out)
    print("Hybrid =", hybrid_out)
    print("True   =", true_out)


    if strict_out != hybrid_out:
        print("\n⚠️ Hybrid differs from strict (expected only on tail edits)")
    else:
        print("✅ Hybrid matches strict (good for unmodified item)")

def edit_tail_byte(serial: str, byte_index: int, new_value: int, *,
                   prefs: dict,
                   encode_mode: str = "true",
                   log_path: str | None = None):
    # pick default lazily so import order never matters
    if log_path is None:
        log_path = LOG_PATH_DEFAULT
    """
    Safely edit one byte, then re-encode with the selected mode:
      - true   : full TRUE re-encode (canonicals, then DP)
      - hybrid : strict mid, TRUE tail
      - strict : original tiling
    Logs to CSV.
    """
    from main import strict_decode_serial

    print("\n[EDIT-TAIL] Editing serial:")
    print("  serial =", serial[:80], "...")
    data, used_blocks, prefix, item_type = strict_decode_serial(serial)

    # compute tail_start (end of last 'mid' block)
    tail_start = sum(B for (L, B, pos) in used_blocks if pos == "mid")
    print(f"  tail_start = {tail_start} (safe edit region: [{tail_start}..{len(data)-1}])")

    if not (0 <= byte_index < len(data)):
        print(f"ERROR: byte_index {byte_index} out of range (len={len(data)})")
        return None
    if byte_index < tail_start and encode_mode != "strict":
        print(f"ERROR: byte_index {byte_index} is in mid region (0..{tail_start-1}). "
              f"Use --encode-mode strict or pick a tail index.")
        return None

    b = bytearray(data)
    old_val = b[byte_index]
    b[byte_index] = new_value
    print(f"  Changed byte[{byte_index}] {old_val} → {new_value}")

    # Capacity check on the containing block (prevents guaranteed overflow)
    cursor = 0
    for (L, B, pos) in used_blocks:
        start, end = cursor, cursor + B
        if start <= byte_index < end:
            chunk = b[start:end]
            max_val = (85 ** L) - 1
            chunk_val = int.from_bytes(chunk, "big")
            print(f"  Block capacity: L={L}, B={B}, max={max_val}, new_val={chunk_val}")
            if chunk_val > max_val and encode_mode == "strict":
                print("  Strict would overflow this block — switch to --encode-mode true/hybrid.")
            break
        cursor = end

    # Re-encode via selected mode
    final = reencode_after_edit(b, used_blocks=used_blocks, prefix=prefix,
                                item_type=item_type, prefs=prefs, encode_mode=encode_mode)
    print(f"\nFINAL ({encode_mode}):\n{final}\n")

    # CSV log
    import csv, pathlib
    row = {
        "serial_head": serial[:12],
        "len_bytes": len(data),
        "tail_start": tail_start,
        "byte_index": byte_index,
        "old_val": old_val,
        "new_val": new_value,
        "encode_mode": encode_mode,
        "new_serial": final or "",
    }
    log_file = pathlib.Path(log_path)
    write_header = not log_file.exists()
    with log_file.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=row.keys())
        if write_header:
            w.writeheader()
        w.writerow(row)
    print(f"[LOG] wrote edit to {log_file}")
    return final


def edit_tail_bytes(serial: str,
                    edits: list[tuple[int, int]],
                    *,
                    prefs: dict,
                    encode_mode: str = "true",
                    allow_mid: bool = False,
                    warn_only: bool = False,
                    log_path: str | None = None):
    if log_path is None:
        log_path = LOG_PATH_DEFAULT
    """
    Safely edit multiple bytes and re-encode with the selected mode.
      - If a byte index falls in 'mid' and allow_mid=False (default), it errors (unless warn_only=True).
      - For STRICT mode, be aware capacity can overflow; TRUE/HYBRID will re-tile as needed.
    """
    from main import strict_decode_serial

    print("\n[EDIT-TAIL] Batch edit:")
    print("  serial =", serial[:80], "...")
    data, used_blocks, prefix, item_type = strict_decode_serial(serial)

    tail_start = sum(B for (L, B, pos) in used_blocks if pos == "mid")
    print(f"  tail_start = {tail_start} (safe edit region: [{tail_start}..{len(data)-1}])")

    b = bytearray(data)
    changes = []
    # Validate and apply edits
    for idx, val in edits:
        if not (0 <= idx < len(b)):
            msg = f"index {idx} out of range (len={len(b)})"
            if warn_only:
                print(f"⚠️ {msg} — skipping")
                continue
            print(f"ERROR: {msg}")
            return None
        if idx < tail_start and not allow_mid and encode_mode != "strict":
            msg = f"index {idx} is in mid region (0..{tail_start-1})"
            if warn_only:
                print(f"⚠️ {msg} — applying anyway due to warn_only=True")
            else:
                print(f"ERROR: {msg}. Use --encode-mode strict or set allow_mid=True.")
                return None
        old = b[idx]
        b[idx] = val
        changes.append((idx, old, val))
        print(f"  Changed byte[{idx}] {old} → {val}")

    # Re-encode via selected mode
    final = reencode_after_edit(b, used_blocks=used_blocks, prefix=prefix,
                                item_type=item_type, prefs=prefs, encode_mode=encode_mode)
    print(f"\nFINAL ({encode_mode}):\n{final}\n")

    # CSV log (one row per change)
    import csv, pathlib
    log_file = pathlib.Path(log_path)
    write_header = not log_file.exists()
    with log_file.open("a", newline="", encoding="utf-8") as f:
        fieldnames = ["serial_head", "len_bytes", "tail_start",
                      "byte_index", "old_val", "new_val",
                      "encode_mode", "new_serial"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            w.writeheader()
        for idx, old, new in changes:
            w.writerow({
                "serial_head": serial[:12],
                "len_bytes": len(data),
                "tail_start": tail_start,
                "byte_index": idx,
                "old_val": old,
                "new_val": new,
                "encode_mode": encode_mode,
                "new_serial": final or "",
            })
    print(f"[LOG] Recorded {len(changes)} edit(s) to {log_file}")
    return final


def swap_tail(serial_base: str, serial_donor: str, prefs):
    """
    Replace the tail block of serial_base with the tail block of serial_donor.
    """
    from main import strict_decode_serial, encode_item_serial

    print("\n[SWAP-TAIL] Grafting donor tail onto base:")
    print("  base  =", serial_base[:80], "...")
    print("  donor =", serial_donor[:80], "...")

    # decode both
    data_base, blocks_base, prefix_base, item_type_base = strict_decode_serial(serial_base)
    data_donor, blocks_donor, prefix_donor, item_type_donor = strict_decode_serial(serial_donor)

    # find mid/tail split
    tail_start_base = sum(B for (L, B, pos) in blocks_base if pos == "mid")
    tail_start_donor = sum(B for (L, B, pos) in blocks_donor if pos == "mid")

    base_mid = data_base[:tail_start_base]
    donor_tail = data_donor[tail_start_donor:]

    combined_bytes = base_mid + donor_tail

    # keep base block layout, but replace tail chunk
    blocks_out = [(L, B) for (L, B, pos) in blocks_base]

    class _Stub:
        def __init__(self, t): self.item_type = t

    new_serial = encode_item_serial(_Stub(item_type_base), combined_bytes, blocks=blocks_out)

    print("\n[RESULT]")
    print("  Old serial =", serial_base)
    print("  Donor tail =", serial_donor)
    print("  New serial =", new_serial)
    return new_serial



if __name__ == "__main__":
    import argparse, sys
    from main import load_true_spec


    parser = argparse.ArgumentParser(description="BL4 True/Strict harness")
    parser.add_argument("--roundtrip", action="store_true", help="Run strict round-trip and derive TRUE spec")
    parser.add_argument("--inspect", type=str, help="Inspect a serial by head")
    parser.add_argument("--test-one", type=str, help="Run a single serial through Strict vs True")
    parser.add_argument("--edit-mode", nargs=3, metavar=("SERIAL", "BYTE_INDEX", "NEW_VALUE"),
                        help="Flip one raw byte and compare encoders")
    parser.add_argument("--compare", nargs=2, metavar=("SERIAL_A", "SERIAL_B"),
                        help="Decode two serials, show byte-by-byte differences.")
    parser.add_argument("--compare-csv", metavar="PATH",
                        help="Optional: write compare() diffs to CSV.")
    parser.add_argument(
        "--encode-mode",
        choices=["true", "hybrid", "strict"],
        default="true",
        help="How to re-encode after edits (default: true)"
    )
    parser.add_argument("--inspect-bytes", metavar="SERIAL",
                        help="Dump every byte with index/dec/hex/ASCII and mid/tail zone.")
    parser.add_argument("--fmt", choices=["dec", "hex", "both"], default="both",
                        help="Value format for --inspect-bytes (default: both).")
    parser.add_argument("--start", type=int, default=None,
                        help="Start index (inclusive) for --inspect-bytes.")
    parser.add_argument("--end", type=int, default=None,
                        help="End index (exclusive) for --inspect-bytes.")
    parser.add_argument("--no-ascii", action="store_true",
                        help="Hide ASCII column in --inspect-bytes.")
    parser.add_argument("--compare-all", action="store_true",
                        help="With --compare, print every index (even matches).")
    parser.add_argument("--compare-fmt", choices=["dec", "hex", "both"], default="both",
                        help="Value format for --compare (default: both).")
    args = parser.parse_args()

    # Reload prefs from JSON if present
    true_spec, prefs = load_true_spec()

    if args.compare:
        sA, sB = args.compare
        compare_bytes(sA, sB, csv_path=args.compare_csv,
                      show_blocks=True, show_all=args.compare_all,
                      fmt=args.compare_fmt)
    if args.inspect_bytes:
        dump_serial_bytes(args.inspect_bytes, fmt=args.fmt,
                          start=args.start, end=args.end,
                          show_ascii=not args.no_ascii)

    if args.roundtrip:
        rc = main()
        sys.exit(rc)

    if args.inspect:
        inspect_serial(args.inspect)
        sys.exit(0)

    if args.test_one:
        s = args.test_one
        test_one_serial(s, prefs)
        sys.exit(0)

    if args.edit_mode:
        serial, idx_str, val_str = args.edit_mode  # or however you parse it
        idx, val = int(idx_str), int(val_str)
        from main import load_true_spec



        _, prefs = load_true_spec()
        edit_tail_byte(serial, idx, val, prefs=prefs, encode_mode=args.encode_mode)
        sys.exit(0)
    parser.print_help()

