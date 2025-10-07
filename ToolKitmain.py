# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Akamoden

import ast
import struct
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
from typing import Dict, List, Optional, Tuple, Union, Set, Any
import json
import pathlib
import math


# BL4 custom Base85 alphabet (as previously observed)
BL4_ALPHABET = "!#$%&()*+-/0123456789;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ^_`abcdefghijklmnopqrstuvwxyz{}~"

# --- per-byte bit-mirror helpers (BL4) ---
def _rev8(x: int) -> int:
    x = ((x & 0xF0) >> 4) | ((x & 0x0F) << 4)
    x = ((x & 0xCC) >> 2) | ((x & 0x33) << 2)
    x = ((x & 0xAA) >> 1) | ((x & 0x55) << 1)
    return x

def _rev_bytes(b: bytes) -> bytes:
    return bytes(_rev8(v) for v in b)

# Known exact block mappings as (symbols -> bytes)
# Keep these canonical; round_trip’s decoder decides what to quarantine.
BLOCKS: List[Tuple[int, int]] = [
    (146, 120),
    (62, 50),
    (53, 43),
    (46, 37),
    (41, 33),
    (26, 21),
    (25, 20),
    (24, 20),
    (23, 19),
    (22, 18),
    (21, 17),
    (20, 16),
    (19, 16),
    (17, 14),
    (16, 13),
    (15, 12),
    (14, 12),
    (12, 10),
    (11, 9),
    (10, 8),
    (9, 8),
    (7, 6),
    (6, 5),
    (5, 4),
    (2, 2),
    (1, 1),
]

# “Tail-only” blocks that must appear only at the very end of the body.
TAIL_ONLY: Set[Tuple[int, int]] = {
    (1,1),(2,2),(5,4),(6,5),(7,6),(9,8),(10,8),(11,9),(12,10),
    (14,12),(17,14),(19,16),(21,17),(22,18),(23,19),(24,20),(25,20)
}

QUARANTINE_BLOCKS: Set[Tuple[int, int]] = set()



TEM_TYPE_PREFIXES = {
    "@Ugct": "torgue_pistol",
    "@Ugr": "grenade",
    "@Uggr": "grenade_mod",
    "@Ugd_t": "grenade",
    "@UgeU": "shield",
    "@Ugw": "weapon_generic",
    # Add more as we catalog them...
}

ITEM_TYPE_HINTS = {
    "RG/": "grenade",
    "Ree": "pistol",
    "RG}": "grenade",
    "RG_{": "shield",
    # Expand from your corpus of serials
}

def dump_bitstream(data: bytes, limit=128):
    """Dump the bitstream of decoded serial bytes."""
    bits = ''.join(f"{b:08b}" for b in data)
    print(f"[BITSTREAM] len={len(bits)} bits")
    print(bits[:limit] + ("..." if len(bits) > limit else ""))
    return bits








def strict_decode_serial(serial: str):
    """
    Strictly decode a full BL4 serial into raw bytes, tiling, and prefix info.

    Returns:
      data        : bytes
      used_blocks : list of (L,B,pos) triples for exact tiling
      prefix      : first 4 chars '@UgX'
      item_type   : the type char after '@Ug'
    """
    if not serial.startswith("@Ug") or len(serial) < 4:
        raise ValueError("Not a valid BL4 serial")

    prefix = serial[:4]
    item_type = serial[3]
    body = serial[4:]

    def extract_fields(data: bytes) -> Dict[str, Any]:
        """
        Clean-room field scan to populate a 'raw_fields' dict for CSV/debugging.
        - Emits 'val16_at_<i>' for little-endian u16 at even offsets (full length).
        - Emits 'byte_<i>' for the first 64 bytes (or len(data), whichever is smaller).
        - Includes a compact 'potential_stats' list of (offset, value) where u16 is in a
          broad, plausible range for gameplay-ish stats.
        - Includes 'potential_flags' as bytes in [0..127] for the first 32 bytes.
        Notes:
          * Key names are preserved for ecosystem compatibility (edit_planner, etc.).
          * The logic and thresholds are our own.
        """
        fields: Dict[str, Any] = {}

        n = len(data)

        # Common 32-bit headers (LE/BE) if available
        if n >= 4:
            fields["header_le"] = int.from_bytes(data[0:4], "little")
            fields["header_be"] = int.from_bytes(data[0:4], "big")
        if n >= 8:
            fields["field2_le"] = int.from_bytes(data[4:8], "little")
        if n >= 12:
            fields["field3_le"] = int.from_bytes(data[8:12], "little")

        # u16 scan (even offsets across entire payload)
        stats16: list[Tuple[int, int]] = []
        for i in range(0, n - 1, 2):
            v = int.from_bytes(data[i:i + 2], "little")
            fields[f"val16_at_{i}"] = v
            # Broad but sane window for "interesting" numbers
            if 50 <= v <= 20000:
                stats16.append((i, v))
        fields["potential_stats"] = stats16

        # First 64 raw bytes & potential flag candidates (low magnitude bytes)
        limit_b = min(n, 64)
        flags: list[Tuple[int, int]] = []
        for i in range(limit_b):
            b = data[i]
            fields[f"byte_{i}"] = b
            if i < 32 and b <= 127:
                flags.append((i, b))
        fields["potential_flags"] = flags

        return fields

    def _pick_from(fields: Dict[str, Any], keys: list[str]):
        """Return the first present value among keys, else None."""
        for k in keys:
            if k in fields:
                return fields[k]
        return None

    def _pick_stat_pair(fields: Dict[str, Any]) -> tuple[Optional[int], Optional[int]]:
        """
        Choose (primary, secondary) from potential_stats with a simple rule:
          - primary = first entry's value
          - secondary = second entry's value (if any)
        """
        ps = fields.get("potential_stats") or []
        if not ps:
            return None, None
        primary = ps[0][1]
        secondary = ps[1][1] if len(ps) > 1 else None
        return primary, secondary

    def decode_weapon(data: bytes, serial: str) -> DecodedItem:
        """
        Clean decoder for item_type 'r' (weapons). Maintains API shape but uses
        neutral heuristics based on our field scan rather than fixed offsets
        from any prior fork.
        """
        fields = extract_fields(data)
        stats = ItemStats()

        # Stats: take the first two plausible u16s as primary/secondary
        stats.primary_stat, stats.secondary_stat = _pick_stat_pair(fields)

        # Common metadata hints (stick with familiar byte positions if present)
        stats.manufacturer = fields.get("byte_4")
        stats.item_class = fields.get("byte_8")
        stats.rarity = fields.get("byte_1")

        # Level: prefer a small value near the early teens if present
        lvl = fields.get("byte_13")
        stats.level = lvl if isinstance(lvl, int) and 1 <= lvl <= 100 else None

        confidence = "high" if len(data) in (20, 21, 24, 26, 33, 37) else "medium"

        return DecodedItem(
            serial=serial,
            item_type='r',
            item_category='weapon',
            length=len(data),
            stats=stats,
            raw_fields=fields,
            confidence=confidence,
        )

    def decode_equipment_e(data: bytes, serial: str) -> DecodedItem:
        """
        Alternate equipment-style decoder for item_type 'e'.
        Uses the same generic stat-pair picking, with different byte hints
        for manufacturer/rarity/class where available.
        """
        fields = extract_fields(data)
        stats = ItemStats()

        stats.primary_stat, stats.secondary_stat = _pick_stat_pair(fields)

        stats.manufacturer = fields.get("byte_1")
        stats.item_class = fields.get("byte_3")
        stats.rarity = fields.get("byte_9")

        # Try a level from early bytes; fallback to a u16 around offset 10 if present
        lvl = fields.get("byte_10")
        if not isinstance(lvl, int) or not (1 <= lvl <= 100):
            lvl = fields.get("val16_at_10")
            lvl = lvl if isinstance(lvl, int) and 1 <= lvl <= 200 else None
        stats.level = lvl

        confidence = "high" if stats.manufacturer is not None else "medium"

        return DecodedItem(
            serial=serial,
            item_type='e',
            item_category='equipment',
            length=len(data),
            stats=stats,
            raw_fields=fields,
            confidence=confidence,
        )

    def decode_equipment_d(data: bytes, serial: str) -> DecodedItem:
        """
        Second equipment variant for item_type 'd'.
        """
        fields = extract_fields(data)
        stats = ItemStats()

        stats.primary_stat, stats.secondary_stat = _pick_stat_pair(fields)

        stats.manufacturer = fields.get("byte_5")
        stats.item_class = fields.get("byte_6")
        stats.rarity = fields.get("byte_14")

        lvl = fields.get("byte_10")
        if not isinstance(lvl, int) or not (1 <= lvl <= 100):
            lvl = fields.get("val16_at_10")
            lvl = lvl if isinstance(lvl, int) and 1 <= lvl <= 200 else None
        stats.level = lvl

        confidence = "medium"

        return DecodedItem(
            serial=serial,
            item_type='d',
            item_category='equipment_alt',
            length=len(data),
            stats=stats,
            raw_fields=fields,
            confidence=confidence,
        )

    def decode_with_blocks(s: str):
        result = []
        char_to_val = {ch: i for i, ch in enumerate(BL4_ALPHABET)}
        n = len(s)
        ordered = sorted(BLOCKS, key=lambda b: -b[0])

        def _rec(pos, out, path):
            if pos == n:
                return bytes(out), path
            rem = n - pos
            for L,B in ordered:
                if (L,B) in TAIL_ONLY and rem != L:
                    continue
                if rem < L:
                    continue
                acc = 0
                try:
                    for ch in s[pos:pos+L]:
                        acc = acc*85 + char_to_val[ch]
                except KeyError:
                    continue
                try:
                    block_bytes = _rev_bytes(acc.to_bytes(B,"big"))
                except OverflowError:
                    continue
                pos_tag = "tail" if pos+L == n else "mid"
                ok = _rec(pos+L, out+block_bytes, path+[(L,B,pos_tag)])
                if ok:
                    return ok
            return None

        out = _rec(0, bytearray(), [])
        if out is None:
            raise ValueError("Failed strict decode: no exact tiling")
        return out

    data, used_blocks = decode_with_blocks(body)
    return data, used_blocks, prefix, item_type

def detect_item_type(serial: str) -> str:
    """
    Try to guess the item type from its prefix and/or substrings.
    """
    for prefix, itype in ITEM_TYPE_PREFIXES.items():
        if serial.startswith(prefix):
            return itype
    for hint, itype in ITEM_TYPE_HINTS.items():
        if hint in serial:
            return itype
    return "unknown"

def _encode_chunk_to_base85(chunk: bytes, sym_len: int, alphabet: str) -> str:
    acc = int.from_bytes(_rev_bytes(chunk), "big")
    digits: List[str] = []
    for _ in range(sym_len):
        acc, rem = divmod(acc, 85)
        digits.append(alphabet[rem])
    if acc != 0:
        # If acc is not zero after producing sym_len digits, chunk needed more digits -> overflow
        raise ValueError(f"Overflow while encoding {len(chunk)}-byte block")
    return "".join(reversed(digits))


def bit_pack_encode(
    data: bytes,
    alphabet: str = BL4_ALPHABET,
    *,
    blocks: Optional[List[Tuple[int, int]]] = None,
    log_blocks: bool = False,
) -> str:
    """
    Strict encoder: packs raw bytes into base-85 using exact BLOCKS only.
    If `blocks` is provided, it enforces that exact tiling (for perfect round-trips).
    """
    out: List[str] = []
    used_blocks: List[Tuple[int, int]] = []

    if blocks is not None:
        # Enforce exact tiling
        offset = 0
        for sym_len, byte_len in blocks:
            if offset + byte_len > len(data):
                raise ValueError(f"Provided blocks exceed data length at offset {offset}")
            out.append(_encode_chunk_to_base85(data[offset : offset + byte_len], sym_len, alphabet))
            used_blocks.append((sym_len, byte_len))
            offset += byte_len
        if offset != len(data):
            raise ValueError(f"Provided blocks total {offset} bytes, but data is {len(data)} bytes")
    else:
        # Greedy by byte_len (still strict, no clamping/guessing)
        i = 0
        ordered = sorted(BLOCKS, key=lambda b: -b[1])  # try larger byte blocks first
        while i < len(data):
            remaining = len(data) - i
            chosen: Optional[Tuple[int, int]] = None
            for sym_len, byte_len in ordered:
                if remaining >= byte_len:
                    chosen = (sym_len, byte_len)
                    break
            if not chosen:
                raise ValueError(f"No block mapping for {remaining} bytes at offset {i}")
            sym_len, byte_len = chosen
            out.append(_encode_chunk_to_base85(data[i : i + byte_len], sym_len, alphabet))
            used_blocks.append(chosen)
            i += byte_len

    if log_blocks:
        print(f"[bit_pack_encode] Used blocks: {used_blocks}")
    return "".join(out)


def bit_pack_decode(s: str, alphabet: str = BL4_ALPHABET, *, return_blocks: bool = False):
    """
    Strict backtracking decoder over exact BLOCKS.
    - No greedy guesses, no clamping.
    - Enforces TAIL_ONLY constraints.
    - If return_blocks=True, returns (bytes, used_blocks) where used_blocks is
      a list of triples (L, B, 'mid'|'tail') in left-to-right order.
    """
    char_to_val = {ch: i for i, ch in enumerate(alphabet)}
    n = len(s)
    ordered = sorted(BLOCKS, key=lambda b: -b[0])  # prefer larger symbol blocks

    def _rec(pos: int, out: bytearray, path: list) -> tuple[bool, bytes | None, list | None]:
        if pos == n:
            return True, bytes(out), path

        remaining = n - pos
        for sym_len, byte_len in ordered:
            # tail-only handling
            if (sym_len, byte_len) in TAIL_ONLY and remaining != sym_len:
                continue
            if remaining < sym_len:
                continue

            # base85 slice -> int
            acc = 0
            try:
                for ch in s[pos:pos+sym_len]:
                    acc = acc * 85 + char_to_val[ch]
            except KeyError:
                continue

            # must fit exactly into byte_len
            try:
                block_bytes = _rev_bytes(acc.to_bytes(byte_len, "big"))
            except OverflowError:
                continue

            new_pos = pos + sym_len
            pos_tag = "tail" if new_pos == n else "mid"

            ok, res_bytes, res_path = _rec(new_pos, out + block_bytes, path + [(sym_len, byte_len, pos_tag)])
            if ok:
                return True, res_bytes, res_path

        return False, None, None

    ok, result, path = _rec(0, bytearray(), [])
    if not ok or result is None:
        raise ValueError("Failed strict decode: no exact block tiling.")

    if return_blocks:
        return result, path
    return result
@dataclass
class ItemStats:
    primary_stat: Optional[int] = None
    secondary_stat: Optional[int] = None
    level: Optional[int] = None
    rarity: Optional[int] = None
    manufacturer: Optional[int] = None
    item_class: Optional[int] = None
    flags: Optional[List[int]] = None


@dataclass
class DecodedItem:
    serial: str
    item_type: str
    item_category: str
    length: int
    stats: ItemStats
    raw_fields: Dict[str, Any]
    confidence: str


def extract_fields(data: bytes) -> Dict[str, Any]:
    fields = {}

    if len(data) >= 4:
        fields['header_le'] = struct.unpack('<I', data[:4])[0]
        fields['header_be'] = struct.unpack('>I', data[:4])[0]

    if len(data) >= 8:
        fields['field2_le'] = struct.unpack('<I', data[4:8])[0]

    if len(data) >= 12:
        fields['field3_le'] = struct.unpack('<I', data[8:12])[0]

    stats_16 = []
    for i in range(0, min(len(data)-1, 20), 2):
        val16 = struct.unpack('<H', data[i:i+2])[0]
        fields[f'val16_at_{i}'] = val16
        if 100 <= val16 <= 10000:
            stats_16.append((i, val16))

    fields['potential_stats'] = stats_16

    flags = []
    for i in range(min(len(data), 20)):
        byte_val = data[i]
        fields[f'byte_{i}'] = byte_val
        if byte_val < 100:
            flags.append((i, byte_val))

    fields['potential_flags'] = flags

    return fields

def decode_weapon(data: bytes, serial: str) -> DecodedItem:
    fields = extract_fields(data)
    stats = ItemStats()

    if 'val16_at_0' in fields:
        stats.primary_stat = fields['val16_at_0']

    if 'val16_at_12' in fields:
        stats.secondary_stat = fields['val16_at_12']

    if 'byte_4' in fields:
        stats.manufacturer = fields['byte_4']

    if 'byte_8' in fields:
        stats.item_class = fields['byte_8']

    if 'byte_1' in fields:
        stats.rarity = fields['byte_1']

    if 'byte_13' in fields and fields['byte_13'] in [2, 34]:
        stats.level = fields['byte_13']

    confidence = "high" if len(data) in [24, 26] else "medium"

    return DecodedItem(
        serial=serial,
        item_type='r',
        item_category='weapon',
        length=len(data),
        stats=stats,
        raw_fields=fields,
        confidence=confidence
    )

def decode_equipment_e(data: bytes, serial: str) -> DecodedItem:
    fields = extract_fields(data)
    stats = ItemStats()

    if 'val16_at_2' in fields:
        stats.primary_stat = fields['val16_at_2']

    if 'val16_at_8' in fields:
        stats.secondary_stat = fields['val16_at_8']

    if 'val16_at_10' in fields and len(data) > 38:
        stats.level = fields['val16_at_10']

    if 'byte_1' in fields:
        stats.manufacturer = fields['byte_1']

    if 'byte_3' in fields:
        stats.item_class = fields['byte_3']

    if 'byte_9' in fields:
        stats.rarity = fields['byte_9']

    confidence = "high" if 'byte_1' in fields and fields['byte_1'] == 49 else "medium"

    return DecodedItem(
        serial=serial,
        item_type='e',
        item_category='equipment',
        length=len(data),
        stats=stats,
        raw_fields=fields,
        confidence=confidence
    )

def decode_equipment_d(data: bytes, serial: str) -> DecodedItem:
    fields = extract_fields(data)
    stats = ItemStats()

    if 'val16_at_4' in fields:
        stats.primary_stat = fields['val16_at_4']

    if 'val16_at_8' in fields:
        stats.secondary_stat = fields['val16_at_8']

    if 'val16_at_10' in fields:
        stats.level = fields['val16_at_10']

    if 'byte_5' in fields:
        stats.manufacturer = fields['byte_5']

    if 'byte_6' in fields:
        stats.item_class = fields['byte_6']

    if 'byte_14' in fields:
        stats.rarity = fields['byte_14']

    confidence = "high" if 'byte_5' in fields and fields['byte_5'] == 15 else "medium"

    return DecodedItem(
        serial=serial,
        item_type='d',
        item_category='equipment_alt',
        length=len(data),
        stats=stats,
        raw_fields=fields,
        confidence=confidence
    )

def decode_other_type(data: bytes, serial: str, item_type: str) -> DecodedItem:
    fields = extract_fields(data)
    stats = ItemStats()

    potential_stats = fields.get('potential_stats', [])
    if potential_stats:
        stats.primary_stat = potential_stats[0][1] if len(potential_stats) > 0 else None
        stats.secondary_stat = potential_stats[1][1] if len(potential_stats) > 1 else None

    if 'byte_1' in fields:
        stats.manufacturer = fields['byte_1']

    if 'byte_2' in fields:
        stats.rarity = fields['byte_2']

    category_map = {
        'w': 'weapon_special',
        'u': 'utility',
        'f': 'consumable',
        '!': 'special'
    }

    return DecodedItem(
        serial=serial,
        item_type=item_type,
        item_category=category_map.get(item_type, 'unknown'),
        length=len(data),
        stats=stats,
        raw_fields=fields,
        confidence="low"
    )

def decode_item_serial(serial: str) -> DecodedItem:
    """
    Decode a BL4 item serial into a structured DecodedItem.
    Returns a DecodedItem with error info if decoding fails.
    """
    try:
        # BL4 serials always start with @Ug + type
        if not serial.startswith('@Ug') or len(serial) < 4:
            raise ValueError("Not a valid BL4 serial")

        payload = serial[4:]  # skip @UgX
        data = bit_pack_decode(payload)

        # item type is the 4th character
        item_type = serial[3]

        if item_type == 'r':
            return decode_weapon(data, serial)
        elif item_type == 'e':
            return decode_equipment_e(data, serial)
        elif item_type == 'd':
            return decode_equipment_d(data, serial)
        else:
            return decode_other_type(data, serial, item_type)


    except (ValueError, KeyError, OverflowError) as err:
        return DecodedItem(
            serial=serial,
            item_type="error",
            item_category="decode_failed",
            length=0,
            stats=ItemStats(),
            raw_fields={"error": str(err)},
            confidence="none",
        )




## --- Signature-robust, blocks-aware encoder shim (PUT AT THE VERY BOTTOM) ----
def _encode_item_serial_strict(decoded_item, data: bytes, blocks=None) -> str:
    """
    Strict encoder that preserves @Ug + item_type (item_type may be empty),
    and (optionally) uses the exact decode tiling to avoid capacity overflows.
    """
    if not hasattr(decoded_item, "item_type"):
        raise ValueError("encode_item_serial requires decoded_item.item_type (can be empty string)")
    item_type = decoded_item.item_type or ""  # allow empty token

    body = bit_pack_encode(bytes(data), alphabet=BL4_ALPHABET, blocks=blocks, log_blocks=False)

    return f"@Ug{item_type}{body}"


def encode_item_serial(*args, **kwargs) -> str:
    """
    Preferred:
        encode_item_serial(decoded_item, data: bytes, blocks=None)

    Back-compat:
        encode_item_serial(decoded_item)  # tries decoded_item.data/payload/raw_bytes/bytes
    """
    # Keyword path
    if "decoded_item" in kwargs and "data" in kwargs:
        return _encode_item_serial_strict(
            kwargs["decoded_item"], kwargs["data"], kwargs.get("blocks")
        )

    # Positional (strict)
    if len(args) >= 2:
        decoded_item, data = args[0], args[1]
        blocks = kwargs.get("blocks", args[2] if len(args) >= 3 else None)
        return _encode_item_serial_strict(decoded_item, data, blocks)

    # Legacy single-arg path
    if len(args) == 1:
        decoded_item = args[0]
        for attr in ("data", "payload", "raw_bytes", "bytes"):
            if hasattr(decoded_item, attr):
                return _encode_item_serial_strict(decoded_item, getattr(decoded_item, attr), kwargs.get("blocks"))
        raise TypeError("encode_item_serial(decoded_item, data[, blocks]) expected — no payload found on decoded_item.")

    raise TypeError("encode_item_serial(decoded_item, data[, blocks]) expected.")


# --- TRUE block rules ---
# Default baseline (used only if true_blocks.json is missing)
def build_allowed_from_blocks(blocks: List[Tuple[int, int]]) -> Dict[int, List[int]]:
    """
    Build allowed_l_by_b from canonical BLOCKS list.
    Groups all symbol lengths L that map to the same byte length B.
    """
    mapping: Dict[int, set[int]] = {}
    for L, B in blocks:
        mapping.setdefault(B, set()).add(L)
    return {B: sorted(Ls) for B, Ls in mapping.items()}

TRUE_BLOCKS_BASELINE = {
    "allowed_l_by_b": build_allowed_from_blocks(BLOCKS),

    # Blocks Gearbox actually uses to close items (tails).
    "tail_only": [
        [1, 1],
        [2, 2],
        [5, 4],
        [6, 5],
        [7, 6],
        [9, 8],
        [10, 8],
        [11, 9],
        [12, 10],
        [14, 12],
        [17, 14],
        [19, 16],
        [21, 17],   # allowed in tail (but may need FORCED_SPLITS override)
        [22, 18],
        [23, 19],
        [24, 20],
        [25, 20],
    ],

    # Larger blocks Gearbox usually uses in the middle of items.
    "mid_only": [
        [26, 21],
        [41, 33],
        [46, 37],
        [53, 43],
        [62, 50],
    ],
}


# Forced overrides for special remainders where Gearbox has a canonical preference.
FORCED_SPLITS = {
    #21: [(25, 20, "mid"), (5, 4, "tail")],
    #35: [(41, 33, "mid"), (2, 2, "tail")],
    #37: [(46, 37, "tail")],
    "23": [[26, 21, "mid"], [2, 2, "tail"]],
    "35": [[41, 33, "mid"], [2, 2, "tail"]]
}

def load_true_spec():
    """
    Load canonical TRUE_BLOCKS + prefs from true_blocks.json if present.
    Returns (true_spec, prefs) with normalized types and canonical prefs.
    Falls back to baseline + canonical normalization if missing.
    """
    path = pathlib.Path("true_blocks.json")
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            true_spec = data.get("true_spec", TRUE_BLOCKS_BASELINE)
            prefs_raw = data.get("prefs", {})

            # --- normalize allowed_l_by_b ---
            alb = true_spec.get("allowed_l_by_b", {})
            norm_alb = {}
            for b_str, Ls in alb.items():
                b = int(b_str)
                norm_alb[b] = sorted({int(x) for x in Ls})
            true_spec["allowed_l_by_b"] = norm_alb

            # ensure 3-byte tails include [2,3,4]
            true_spec["allowed_l_by_b"][3] = [2, 3, 4]

            # --- normalize tail_only / mid_only ---
            def _norm_pairs(seq):
                out = []
                for pair in seq or []:
                    L, B = int(pair[0]), int(pair[1])
                    out.append((L, B))
                return sorted(set(out))

            true_spec["tail_only"] = list(_norm_pairs(true_spec.get("tail_only")))
            true_spec["mid_only"]  = list(_norm_pairs(true_spec.get("mid_only")))
            mid_set = set(true_spec["mid_only"])
            tail_set = set(true_spec["tail_only"])
            both = mid_set & tail_set
            if both:
                true_spec["tail_only"] = sorted(tail_set - both)

            # --- normalize prefs ---
            prefs: Dict[Tuple[int, str], List[int]] = {}
            for k, v in prefs_raw.items():
                try:
                    B_str, pos = k.split(":")
                    B = int(B_str)
                    Ls = [int(x) for x in v]
                    prefs[(B, pos)] = Ls
                except Exception:
                    continue

            # canonical normalization for 3-byte tail blocks
            prefs[(3, "tail")] = [2, 3, 4]
            print("[DEBUG load_true_spec] normalized (3,'tail') prefs =", prefs.get((3, "tail")))

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

            return true_spec, prefs

    # --- fallback if no JSON exists ---
    true_spec = TRUE_BLOCKS_BASELINE.copy()
    # make sure 3-byte tails include all 2,3,4 forms
    true_spec["allowed_l_by_b"][3] = [2, 3, 4]

    prefs: Dict[Tuple[int, str], List[int]] = {}
    prefs[(3, "tail")] = [2, 3, 4]

    return true_spec, prefs

# ---------------------------------------------------------------------------
# Preferred digit lengths (tie-breakers) for TRUE encoder
# ---------------------------------------------------------------------------
PREFERRED_L_BY_B = {
    2: 3,    # prefer 3 digits for 2-byte blocks
    4: 4,
    8: 8,
    12: 12,
    14: 14,
    16: 19,  # prefer 19 over 20
    18: 18,
    19: 19,
    20: 19,  # force fallback to 19
    42: 43,  # prefer 43 when 42/43 both valid
    43: 43,
}
    
    # --- keep your existing imports/constants above ---
    
    # HELPERS (already in your file; shown here for completeness)
def _base85_digits_from_int(acc: int) -> list[int]:
    """Return base85 digits (most-significant first) with no leading zeros."""
    if acc == 0:
        return [0]
    digits = []
    while acc:
        acc, r = divmod(acc, 85)
        digits.append(r)
    return list(reversed(digits))

def _int_from_bytes_be(chunk: bytes) -> int:
    acc = 0
    for b in chunk:
        acc = (acc << 8) | b
    return acc

def _encode_digits_to_symbols(digits: list[int], alphabet: str) -> str:
    return "".join(alphabet[d] for d in digits)

# ---- TRUE encoder with per-position L preferences & debug tracing ----
from collections import Counter
forced_split_usage = Counter()


# --- TRUE encoder implementation tag ---
TRUE_IMPL_TAG = "DP_v4_json_stable_cli"

# --- Canonical overrides (JSON) ---
CANONICAL_OVERRIDES = {}
_OVERRIDES_LOADED = False

def load_canonical_overrides():
    """Load canonical override tilings from canonical_overrides.json if it exists."""
    import json, os
    global CANONICAL_OVERRIDES
    path = os.path.join(os.path.dirname(__file__), "canonical_overrides.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                ov = json.load(f) or {}
            # normalize keys to int if needed
            CANONICAL_OVERRIDES.update({int(k): v for k, v in ov.items()})
            print(f"[INFO] Loaded {len(CANONICAL_OVERRIDES)} canonical overrides from canonical_overrides.json")
        except Exception as e:
            print(f"[WARN] Failed to load canonical_overrides.json: {e}")
    # else: leave dict empty (no noise)

    # --- TRUE helpers (extracted) ---



def _true_fits_capacity(chunk: bytes, L: int, B: int) -> bool:
    """Return True if packer emits exactly L base85 digits for this (L,B) capacity."""
    try:
        seg = bit_pack_encode(chunk, alphabet=BL4_ALPHABET, blocks=[(L, len(chunk))])
        return len(seg) == L
    except Exception:
        return False

def _true_enc_block(chunk: bytes, L: int, pos_tag: str) -> str:
    """Emit base85 using the game's alphabet. Includes the 3-byte tail (L=2) quirk).""" 
    # Mirror bits per BL4 rule before interpreting
    mchunk = _rev_bytes(chunk)
    if len(mchunk) == 3 and pos_tag == "tail" and L == 2:
        # 3-byte tail closed with 2 digits uses the last 2 mirrored bytes
        acc2 = int.from_bytes(mchunk[1:], "big")
        d1 = acc2 % 85
        d2 = (acc2 // 85) % 85
        return BL4_ALPHABET[d2] + BL4_ALPHABET[d1]
    return _encode_chunk_to_base85(mchunk, L, BL4_ALPHABET)

def _true_try_seq(data: bytes, n: int, seq, allowed_l_by_b, mid_only, tail_only, quarantine):
    """Try an explicit canonical sequence [(L,B,pos), ...]. Return encoded string or None."""
    j = 0
    out = []
    for (L, B, pos_tag) in seq:
        if j + B > n:
            return None
        pair = (L, B)
        if pos_tag == "tail" and pair in mid_only:
            print(f"[OVERRIDE_FAIL] {(L,B,pos_tag)} forbidden (mid_only)")
            return None
        if pos_tag == "mid" and pair in tail_only:
            print(f"[OVERRIDE_FAIL] {(L,B,pos_tag)} forbidden (tail_only)")
            return None
        if pair in quarantine:
            return None
        chunk = data[j:j+B]
        if not _true_fits_capacity(chunk, L, B):
            print(f"[OVERRIDE_FAIL] capacity {(L, B, pos_tag)}")
            return None
        out.append(_true_enc_block(chunk, L, pos_tag))
        j += B
    if j != n:
        return None
    return "".join(out)

class _TrueDPSolver:
    """
    Encapsulates the DP search so true_encode() stays readable.
    Implements tie-breakers:
      - minimize total L (encoded length)
      - prefer single-block (fewer segments)
      - tail: prefer B=4 over B=2
      - larger B earlier
      - larger L earlier
    """
    def __init__(self, data, allowed_l_by_b, mid_only, tail_only, quarantine):
        self.data = data
        self.n = len(data)
        self.allowed_l_by_b = allowed_l_by_b
        self.mid_only = mid_only
        self.tail_only = tail_only
        self.quarantine = quarantine
        self.memo = {}  # idx -> best tuple

    def solve(self, i: int):
        if i == self.n:
            return (0, 0, 0, (), (), "", ())
        if i in self.memo:
            return self.memo[i]

        best = None
        rem = self.n - i

        # larger B first
        for B in sorted(self.allowed_l_by_b.keys(), reverse=True):
            if B > rem:
                continue

            j = i + B
            pos_tag = "tail" if j == self.n else "mid"

            # filter L candidates for this B/pos
            cand_Ls = []
            for L in self.allowed_l_by_b[B]:
                pair = (L, B)
                if pair in self.quarantine:
                    continue
                if pos_tag == "tail" and pair in self.mid_only:
                    continue
                if pos_tag == "mid" and pair in self.tail_only:
                    continue
                cand_Ls.append(L)
            if not cand_Ls:
                continue

            chunk = self.data[i:j]
            # larger L first
            for L in sorted(set(cand_Ls), reverse=True):
                if not _true_fits_capacity(chunk, L, B):
                    continue

                seg = _true_enc_block(chunk, L, pos_tag)
                sub = self.solve(j)
                if sub is None:
                    continue

                (sub_len, sub_cnt, sub_tail_pref,
                 sub_B_vec, sub_L_vec, sub_out, sub_trace) = sub

                total_len  = L + sub_len
                blocks_cnt = 1 + sub_cnt

                # tail pref: prefer B=4 (smaller), penalize B=2 (larger)
                tail_pref = sub_tail_pref
                if pos_tag == "tail":
                    tail_pref += 1 if B == 2 else (-1 if B == 4 else 0)

                early_B_vec = (-B,) + sub_B_vec
                early_L_vec = (-L,) + sub_L_vec

                cand = (total_len, blocks_cnt, tail_pref,
                        early_B_vec, early_L_vec,
                        seg + sub_out,
                        ((L, B, pos_tag),) + sub_trace)

                if best is None or cand < best:
                    best = cand

        self.memo[i] = best  # may be None (dead end)
        return best



def true_encode(
    data: bytes,
    item_type: str = "",
    *,
    prefix: str | None = None,
    prefs: dict | None = None,
    debug_collect: list | None = None
) -> str:
    """
    Gearbox-true encoder with JSON canonical overrides and DP search.
    Applies canonical overrides (JSON first, then FORCED_SPLITS) before DP.
    """
    if prefix is None:
        prefix = f"@Ug{item_type}"

    # Load spec and prefs
    true_spec, auto_prefs = load_true_spec()
    allowed_l_by_b = {int(b): list(v) for b, v in true_spec["allowed_l_by_b"].items()}
    tail_only = {(L, B) for (L, B) in true_spec.get("tail_only", [])}
    mid_only  = {(L, B) for (L, B) in true_spec.get("mid_only", [])}
    if not prefs:
        prefs = auto_prefs or {}

    n = len(data)

    # Load canonical overrides (once) if available
    try:
        global _OVERRIDES_LOADED
        if '_OVERRIDES_LOADED' not in globals():
            _OVERRIDES_LOADED = False
        if not _OVERRIDES_LOADED and 'load_canonical_overrides' in globals():
            load_canonical_overrides()
            _OVERRIDES_LOADED = True
    except Exception:
        pass  # optional

    # --- Canonical overrides first (JSON takes precedence, then FORCED_SPLITS) ---
    seq = None
    if 'CANONICAL_OVERRIDES' in globals():
        seq = CANONICAL_OVERRIDES.get(n)
    if seq is None and 'FORCED_SPLITS' in globals():
        seq = FORCED_SPLITS.get(n)

    if seq:
        out = _true_try_seq(
            data, n, seq,
            allowed_l_by_b=allowed_l_by_b,
            mid_only=mid_only,
            tail_only=tail_only,
            quarantine=QUARANTINE_BLOCKS
        )
        if out is not None:
            if debug_collect is not None:
                debug_collect.append({"decision": "override_seq", "seq": list(seq)})
            return prefix + out
        else:
            print(f"[WARN] Canonical override for {n} bytes failed, falling back to DP")

    # --- DP search (global) ---
    solver = _TrueDPSolver(
        data=data,
        allowed_l_by_b=allowed_l_by_b,
        mid_only=mid_only,
        tail_only=tail_only,
        quarantine=QUARANTINE_BLOCKS
    )
    ans = solver.solve(0)
    if ans is None:
        raise RuntimeError(f"TRUE search failed: no tiling (n={n}). "
                           f"Check quarantine/mid/tail-only for a tail that can close {n}.")

    total_len, blocks_count, tail_pref, early_B_vec, early_L_vec, out_str, trace = ans
    if debug_collect is not None:
        debug_collect.append({
            "decision": "dp_seq",
            "impl": TRUE_IMPL_TAG,
            "cost": total_len,
            "tie": (blocks_count, tail_pref, early_B_vec, early_L_vec),
            "seq": list(trace)
        })
    return prefix + out_str


if __name__ == "__main__":
    print(f"[INFO] Loaded FORCED_SPLITS: {FORCED_SPLITS}")


from typing import Any, Dict, Optional, Tuple

