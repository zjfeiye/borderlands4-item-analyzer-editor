import {b85Decode} from "./lib/b85.js";
import {hexToBin} from "./lib/hex_to_bin.js";
import {listCommonPatterns} from "./lib/list_common_patterns.js"
import {sortByLengthAscending} from "./lib/sort_by_length.js"

let item1 = hexToBin(b85Decode('@Ugy3L+2}TYg%$yC%i7M2gZldO)@}cgb!l34$a-qf{00'));
let item2 = hexToBin(b85Decode('@Ugy3L+2}Ta0Od!I{*`S=LLLKTRY91;d>K-Z#Y7QzFY8(O'));

/**
 * OPTIMIZED: Uses modern array methods for cleaner and more efficient reconstruction.
 */
function trySplitPart(parts, pattern) {
    const results = [];
    parts.forEach((part, i) => {
        if (part[1]) return; // Already matched part, skip

        const pos = part[0].indexOf(pattern);
        if (pos === -1) return; // Pattern not found in this part

        // Found pattern in this part, split it
        const before = part[0].substring(0, pos);
        const after = part[0].substring(pos + pattern.length);

        const newParts = [...parts.slice(0, i)]; // Parts before this one

        if (before.length > 0) newParts.push([before, false]);
        newParts.push([pattern, true]); // The matched part
        if (after.length > 0) newParts.push([after, false]);

        newParts.push(...parts.slice(i + 1)); // Parts after this one
        results.push(newParts);
    });
    return results;
}

// This helper function is fine as is
function detectEndOfRecursion(shortestPatternLength, parts) {
    let atLeastOneFreePart = false;
    for (const part of parts) {
        if (!part[1]) {
            atLeastOneFreePart = true;
            if (part[0].length >= shortestPatternLength) return false; // A match is still possible
        }
    }
    return !atLeastOneFreePart; // If no free parts, we are done
}



// --- Main Execution ---
const commonPatterns = listCommonPatterns(item1, item2, 24);
sortByLengthAscending(commonPatterns);

let allMatches = [];
function match(patternIndex, parts1, parts2, depth) {
    // No more patterns to try
    if (patternIndex >= commonPatterns.length) {
        allMatches.push(JSON.stringify([parts1, parts2]));
        return;
    }

    // Check for early termination
    const shortestPatternLength = commonPatterns[patternIndex].length;
    if (detectEndOfRecursion(shortestPatternLength, parts1) || detectEndOfRecursion(shortestPatternLength, parts2)) {
        allMatches.push(JSON.stringify([parts1, parts2]));
        return;
    }

    for (let i = patternIndex; i < commonPatterns.length; i++) {
        if (depth === 0) {
            console.log(`Top level, trying pattern ${i + 1} of ${commonPatterns.length}`);
        }
        const pattern = commonPatterns[i];

        const matched1 = trySplitPart(parts1, pattern);
        if (matched1.length === 0 || matched1.length >= 3) continue;

        const matched2 = trySplitPart(parts2, pattern);
        if (matched2.length === 0 || matched2.length >= 3) continue;

        console.log(depth, matched1.length, matched2.length);

        for (const p1 of matched1) {
            for (const p2 of matched2) {
                // Recursive call passes the *next index* instead of a new, sliced array
                // console.log(depth, p1, p2);
                match(i + 1, p1, p2, depth + 1);
            }
        }
    }
}

match(0, [[item1, false]], [[item2, false]], 0);
