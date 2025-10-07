/**
 * Aligns two strings using an algorithm with an affine gap penalty.
 * This prioritizes grouping gaps together rather than scattering them.
 * @param {string} seqA The first sequence.
 * @param {string} seqB The second sequence.
 * @param {number} matchScore Score for a match.
 * @param {number} mismatchPenalty Penalty for a mismatch.
 * @param {number} gapOpenPenalty Penalty for starting a gap.
 * @param {number} gapExtendPenalty Penalty for extending a gap.
 * @returns {object} An object with aligned sequences, comparison string, and stats.
 */
function affineGapAlignment(seqA, seqB, matchScore = 5, mismatchPenalty = -4, gapOpenPenalty = -15, gapExtendPenalty = -2) {
    const lenA = seqA.length;
    const lenB = seqB.length;

    // 1. Initialize three DP matrices
    // M: Score ending with a match/mismatch
    // Ix: Score ending with a gap in seqB
    // Iy: Score ending with a gap in seqA
    const M = Array(lenA + 1).fill(null).map(() => Array(lenB + 1).fill(-Infinity));
    const Ix = Array(lenA + 1).fill(null).map(() => Array(lenB + 1).fill(-Infinity));
    const Iy = Array(lenA + 1).fill(null).map(() => Array(lenB + 1).fill(-Infinity));

    M[0][0] = 0;

    for (let i = 1; i <= lenA; i++) {
        Ix[i][0] = gapOpenPenalty + (i - 1) * gapExtendPenalty;
    }
    for (let j = 1; j <= lenB; j++) {
        Iy[0][j] = gapOpenPenalty + (j - 1) * gapExtendPenalty;
    }

    // 2. Fill the matrices
    for (let i = 1; i <= lenA; i++) {
        for (let j = 1; j <= lenB; j++) {
            const score = seqA[i - 1] === seqB[j - 1] ? matchScore : mismatchPenalty;

            M[i][j] = score + Math.max(M[i - 1][j - 1], Ix[i - 1][j - 1], Iy[i - 1][j - 1]);
            Ix[i][j] = Math.max(M[i - 1][j] + gapOpenPenalty, Ix[i - 1][j] + gapExtendPenalty);
            Iy[i][j] = Math.max(M[i][j - 1] + gapOpenPenalty, Iy[i][j - 1] + gapExtendPenalty);
        }
    }

    // 3. Traceback
    let alignedA = '';
    let alignedB = '';
    let i = lenA;
    let j = lenB;

    let scoreM = M[i][j];
    let scoreIx = Ix[i][j];
    let scoreIy = Iy[i][j];

    const _M = 0, _Ix = 1, _Iy = 2;

    let currentMatrix;
    if (scoreM >= scoreIx && scoreM >= scoreIy) {
        currentMatrix = _M;
    } else if (scoreIx >= scoreIy) {
        currentMatrix = _Ix;
    } else {
        currentMatrix = _Iy;
    }

    while (i > 0 || j > 0) {
        if (currentMatrix === _M) {
            const score = (i > 0 && j > 0 && seqA[i - 1] === seqB[j - 1]) ? matchScore : mismatchPenalty;
            alignedA = seqA[i - 1] + alignedA;
            alignedB = seqB[j - 1] + alignedB;

            const prevM = M[i - 1][j - 1];
            const prevIx = Ix[i - 1][j - 1];

            if (M[i][j] === score + prevM) {
                currentMatrix = _M;
            } else if (M[i][j] === score + prevIx) {
                currentMatrix = _Ix;
            } else {
                currentMatrix = _Iy;
            }
            i--;
            j--;
        } else if (currentMatrix === _Ix) {
            alignedA = seqA[i - 1] + alignedA;
            alignedB = ' ' + alignedB;

            if (Ix[i][j] === M[i - 1][j] + gapOpenPenalty) {
                currentMatrix = _M;
            } else {
                currentMatrix = _Ix;
            }
            i--;
        } else { // currentMatrix === _Iy
            alignedA = ' ' + alignedA;
            alignedB = seqB[j - 1] + alignedB;

            if (Iy[i][j] === M[i][j - 1] + gapOpenPenalty) {
                currentMatrix = _M;
            } else {
                currentMatrix = _Iy;
            }
            j--;
        }
    }

    // 4. Generate comparison string and stats
    let comparison = '';
    let matches = 0, differences = 0, additions = 0;

    for (let k = 0; k < alignedA.length; k++) {
        if (alignedA[k] === alignedB[k]) {
            comparison += '=';
            matches++;
        } else if (alignedA[k] === ' ' || alignedB[k] === ' ') {
            comparison += '+';
            additions++;
        } else {
            comparison += '!';
            differences++;
        }
    }

    let total = matches + differences + additions;

    // Replace spaces by nbsp
    alignedA = alignedA.replace(/ /g, '\u00A0');
    alignedB = alignedB.replace(/ /g, '\u00A0');

    return {
        alignedA,
        alignedB,
        comparison,
        stats: { matches, differences, additions, total }
    };
}

export { affineGapAlignment };
