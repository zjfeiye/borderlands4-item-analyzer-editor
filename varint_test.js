/**
 * Borderlands 4 "serial" reader (read-only, no encoding).
 *
 * What it does:
 * - Hex string -> Uint8Array
 * - Finds a plausible header marker 0x22, reads a 1-byte header length L, then parses:
 *   - Header: L bytes of (tag byte + varint) pairs
 *   - Body:   remaining bytes as (tag byte + varint) pairs
 * - Produces offsets, raw bytes, and normalized integers (numbers or BigInt if needed)
 *
 * Assumptions (based on provided samples and experiments):
 * - There is typically a small preamble before a 0x22 header marker.
 * - The header length fits in one byte (0..255). (All supplied samples fit this.)
 * - Each field is: 1-byte tag, followed by a base-128 varint (LEB128 style).
 * - No checksums.
 *
 * This reader is deliberately conservative:
 * - If no plausible 0x22 header is found, it parses the entire payload
 *   as a tag+varint stream and marks the header as "absent".
 * - If a varint is truncated, it records a warning and stops at the last good field.
 *
 * Usage:
 *   const result = parseSerialHex("8060e084220e46092a0bdc0ca1d42a8d48a8b512448543f5aa0e6a75021cea16");
 *   console.log(result);
 */

///////////////////////////
// Low-level utilities
///////////////////////////

/** Convert a hex string (with or without spaces) to a Uint8Array. */
function hexToBytes(hex) {
    if (typeof hex !== "string") {
        throw new TypeError("hex must be a string");
    }
    const clean = hex.replace(/\s+/g, "").toLowerCase();
    if (clean.length % 2 !== 0) {
        throw new Error("hex length must be even");
    }
    const out = new Uint8Array(clean.length / 2);
    for (let i = 0; i < out.length; i++) {
        const byte = clean.slice(i * 2, i * 2 + 2);
        const v = Number.parseInt(byte, 16);
        if (Number.isNaN(v)) {
            throw new Error(`invalid hex at byte ${i}: "${byte}"`);
        }
        out[i] = v;
    }
    return out;
}

/**
 * Read a base-128 varint (LEB128 style) from bytes at offset.
 * Returns { value, bytesRead, truncated, rawBytes }.
 *
 * - "value" is a Number if <= Number.MAX_SAFE_INTEGER, otherwise BigInt.
 * - "truncated" is true if the varint hit end-of-buffer before termination bit.
 */
function readVarint(bytes, offset) {
    let shift = 0n;
    let n = 0n;
    let bytesRead = 0;
    const raw = [];

    for (let i = offset; i < bytes.length; i++) {
        const b = bytes[i];
        raw.push(b);
        bytesRead++;
        const data = BigInt(b & 0x7f);
        n |= (data << shift);
        if ((b & 0x80) === 0) {
            // done
            const maxSafe = BigInt(Number.MAX_SAFE_INTEGER);
            const value = n <= maxSafe ? Number(n) : n;
            return { value, bytesRead, truncated: false, rawBytes: Uint8Array.from(raw) };
        }
        shift += 7n;
        // guard against absurdly long varints
        if (bytesRead > 10) {
            // 10 bytes already encodes > 64 bits; consider it malformed
            const maxSafe = BigInt(Number.MAX_SAFE_INTEGER);
            const value = n <= maxSafe ? Number(n) : n;
            return { value, bytesRead, truncated: true, rawBytes: Uint8Array.from(raw) };
        }
    }

    // reached end without termination
    const maxSafe = BigInt(Number.MAX_SAFE_INTEGER);
    const value = n <= maxSafe ? Number(n) : n;
    return { value, bytesRead, truncated: true, rawBytes: Uint8Array.from(raw) };
}

/** Format a small byte slice as hex (for diagnostics). */
function bytesToHex(bytes, start = 0, end = bytes.length) {
    const parts = [];
    for (let i = start; i < end; i++) {
        parts.push(bytes[i].toString(16).padStart(2, "0"));
    }
    return parts.join("");
}

///////////////////////////
// Header discovery
///////////////////////////

/**
 * Find a plausible header marker 0x22 within the first few bytes.
 * We require:
 * - marker byte 0x22
 * - a following length byte L
 * - and that "L bytes" of header payload actually fit in the buffer
 *
 * Returns { markerIndex, headerLen } or null if none plausible.
 *
 * Strategy:
 * - Search index range [0..min(12, bytes.length-2)] for 0x22
 * - Read L = bytes[i+1]
 * - Validate i+2+L <= bytes.length
 */
function findHeader(bytes) {
    const searchLimit = Math.min(12, Math.max(0, bytes.length - 2));
    for (let i = 0; i <= searchLimit; i++) {
        if (bytes[i] === 0x22) {
            const L = bytes[i + 1];
            if (i + 2 + L <= bytes.length) {
                return { markerIndex: i, headerLen: L };
            }
        }
    }
    return null;
}

///////////////////////////
// Tag+Varint stream parser
///////////////////////////

/**
 * Parse a stream of (tag byte + varint value) pairs from [offset .. end).
 * Stops at the first error or end. Returns entries + diagnostics.
 *
 * Each entry:
 * {
 *   tag: number,
 *   tagOffset: number,
 *   value: number|bigint,
 *   valueBytes: Uint8Array,
 *   valueOffset: number,
 *   totalBytes: number
 * }
 */
function parseTagVarintStream(bytes, offset, end) {
    const entries = [];
    const warnings = [];
    let pos = offset;

    while (pos < end) {
        const tagOffset = pos;
        const tag = bytes[pos++];
        if (pos >= end) {
            warnings.push({
                kind: "truncated_value",
                message: "Tag at end of buffer has no following varint.",
                tagOffset
            });
            break;
        }

        const { value, bytesRead, truncated, rawBytes } = readVarint(bytes, pos);
        if (pos + bytesRead > end) {
            // varint spills beyond permitted end
            warnings.push({
                kind: "truncated_value",
                message: "Varint spills beyond declared region.",
                tagOffset,
                valueOffset: pos
            });
            break;
        }

        entries.push({
            tag,
            tagOffset,
            value,
            valueBytes: rawBytes,
            valueOffset: pos,
            totalBytes: 1 + bytesRead
        });

        pos += bytesRead;

        if (truncated) {
            warnings.push({
                kind: "truncated_value",
                message: "Encountered truncated varint; stopping parse at last good entry.",
                tagOffset
            });
            break;
        }
    }

    return { entries, endOffset: pos, warnings };
}

///////////////////////////
// Top-level parse
///////////////////////////

/**
 * Parse a Borderlands-4-style serial hex string.
 * Returns a structured object describing:
 * - preamble (bytes before header marker, if any)
 * - header block (if found)
 * - body stream
 * - global warnings
 */
function parseSerialHex(hex) {
    const bytes = hexToBytes(hex);
    const warnings = [];
    let headerInfo = findHeader(bytes);

    if (!headerInfo) {
        // No plausible header found. Parse whole buffer as a stream.
        const body = parseTagVarintStream(bytes, 0, bytes.length);
        warnings.push({
            kind: "no_header_found",
            message:
                "No plausible 0x22 header marker found in the first bytes. Parsed entire payload as a tag+varint stream."
        });

        return {
            ok: true,
            length: bytes.length,
            bytes,
            preamble: { start: 0, end: 0, hex: "" },
            header: null,
            body: {
                start: 0,
                end: body.endOffset,
                entries: body.entries
            },
            warnings: warnings.concat(body.warnings)
        };
    }

    const { markerIndex, headerLen } = headerInfo;
    const preamble = {
        start: 0,
        end: markerIndex,
        hex: bytesToHex(bytes, 0, markerIndex)
    };

    const headerStart = markerIndex + 2;
    const headerEnd = headerStart + headerLen;

    // Parse header payload as stream of tag+varint pairs
    const headerParse = parseTagVarintStream(bytes, headerStart, headerEnd);

    if (headerParse.endOffset !== headerEnd) {
        warnings.push({
            kind: "header_parse_boundary",
            message:
                "Header parse ended before the declared end; remaining bytes ignored.",
            expectedEnd: headerEnd,
            actualEnd: headerParse.endOffset
        });
    }

    // Parse remainder (post-header) as stream
    const bodyStart = headerEnd;
    const bodyParse = parseTagVarintStream(bytes, bodyStart, bytes.length);

    return {
        ok: true,
        length: bytes.length,
        bytes,
        preamble,
        headerMarker: {
            offset: markerIndex,
            markerByte: 0x22,
            lengthByte: headerLen
        },
        header: {
            start: headerStart,
            end: headerEnd,
            length: headerLen,
            entries: headerParse.entries
        },
        body: {
            start: bodyStart,
            end: bodyParse.endOffset,
            entries: bodyParse.entries
        },
        warnings: warnings.concat(headerParse.warnings, bodyParse.warnings)
    };
}

///////////////////////////
// Pretty-printers (optional)
///////////////////////////

/** Human-ish summary of entries. */
function summarizeEntries(entries) {
    return entries.map(e => {
        const v =
            typeof e.value === "bigint"
                ? `${e.value.toString()}n`
                : String(e.value);
        return `@0x${e.tagOffset.toString(16).padStart(4, "0")} tag=0x${e.tag
            .toString(16)
            .padStart(2, "0")}  value=${v}  (valueBytes=${bytesToHex(
            e.valueBytes
        )})`;
    });
}

/** Pretty print a full parsed object (for inspection). */
function prettyPrintParsed(parsed) {
    const lines = [];
    lines.push(`length: ${parsed.length} bytes`);
    if (parsed.header) {
        lines.push(
            `preamble: [0..${parsed.preamble.end - 1}] hex=${parsed.preamble.hex}`
        );
        lines.push(
            `header marker @0x${parsed.headerMarker.offset
                .toString(16)
                .padStart(4, "0")} len=${parsed.header.length}`
        );
        lines.push(
            `header entries (${parsed.header.entries.length}):\n` +
            summarizeEntries(parsed.header.entries).join("\n")
        );
        lines.push(
            `body entries (${parsed.body.entries.length}):\n` +
            summarizeEntries(parsed.body.entries).join("\n")
        );
    } else {
        lines.push(`no header; parsed body as entire payload`);
        lines.push(
            `body entries (${parsed.body.entries.length}):\n` +
            summarizeEntries(parsed.body.entries).join("\n")
        );
    }

    if (parsed.warnings.length) {
        lines.push(
            `warnings:\n` +
            parsed.warnings
                .map(
                    w =>
                        `- ${w.kind}: ${w.message || ""} ${w.tagOffset ? `(offset=0x${w.tagOffset.toString(16)})` : ""}`
                )
                .join("\n")
        );
    }
    return lines.join("\n");
}

///////////////////////////
// Example (you can remove this)
///////////////////////////

const sample = "8060e084220e4609950a925c51aa1546a3d45a87a1eea1f2353aa1e6750b75070e01";
const parsed = parseSerialHex(sample);
console.log(prettyPrintParsed(parsed));

/*
 * Export for module environments:
 * module.exports = { parseSerialHex, hexToBytes, readVarint, prettyPrintParsed };
 */
