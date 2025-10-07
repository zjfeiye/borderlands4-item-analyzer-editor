import {b85Decode, b85Encode, base85ChangeByteOrder} from './lib/b85.js';
import {affineGapAlignment} from "./lib/affineGapAlignment.js";
import {hexToBin} from "./lib/hex_to_bin.js";

let buybacks = [[
    '@Ugy3L+2}TYg%$yC%i7M2gZldO)@}cgb!l34$a-qf{00',
    '@Ugy3L+2}Ta0Od!I{*`S=LLLKTRY91;d>K-Z#Y7QzFY8(O'
], [
    '@Ugy3L+2}TYgOyvyviz?KiBDJYGs9dOW2m',
    '@Ugy3L+2}Ta0Od!Hk&Y-`jLLDkno0@~lg(`;t'
], [
    '@Ugy3L+2}TYgjMogxi7Hg07IhPq4>b?9sX3@zs9y*',
    '@Ugy3L+2}Ta0Od!H/&7hp9LM3WZH&OXe^H7_bgUW^ag#Z'
], [
    '@Ugy3L+2}TYgjN}O_jVjck8kML=-9yboeX0!V4k{Na9I7P(',
    '@Ugy3L+2}Ta0Od!HYo}kjGLLI76iF(vM)I8Lu%AoF`a-qVZS/R`'
], [
    '@Ugct)%FmVuJXn{hb3U#POJ!&6nQ*lsxP_0lm5d',
    '@Ugct)%FmVuN0uhE5C^V{2hg#I5_MtWv2ek*)3Uw0!'
], [
    '@UgzR8/2__CAOuq;Eiz?Kj9yO^ss8y(TsD20',
    '@UgzR8/2__DrOd!Jad!WClLM`f1lbVBCg=&ZDhX4'
], [
    '@UgcJizFmVuJFlEqRRG}I*bSP4ldV~6d`h_Zs00',
    '@UgcJizFmVuN0ucsN2K_}9s!>CSB2}q3s6VJ*sImw'
]];

let similar_items = [
    '@Ugy3L+2}TYg%$yC%i7M2gZldO)@}cgb!l34$a-qf{00',
    '@Ugy3L+2}TYgT#^cvMir`2hg#I5@}cgb=Ak+@2XzZ/4gm',
    '@Ugy3L+2}TYgOyvyviz?KiBDJYGs9dOW2m',
    '@Ugy3L+2}TYgjMogxi7Hg07IhPq4>b?9sX3@zs9y*',
    '@Ugy3L+2}TYg4BQJUjVjck61AvE^+Sb3b!rZ(7U~=V',
];

let similar_items_combinations = [];
for (let i = 0; i < similar_items.length; i++)
    for (let j = 0; j < similar_items.length; j++)
        if (i !== j)
            similar_items_combinations.push([similar_items[i], similar_items[j]]);

let items;
// items = similar_items_combinations;
items = buybacks;

let stats = {};

for (let i = 0; i < 4; i++) {
    for (let j = 0; j < 4; j++) {
        for (let k = 0; k < 4; k++) {
            for (let l = 0; l < 4; l++) {
                if (i === j || i === k || i === l || j === k || j === l || k === l)
                    continue;

                let byteOrder = [i, j, k, l];
                let key = byteOrder + '';
                base85ChangeByteOrder(byteOrder);

                for (let [rawOriginal, rawBuyback] of items) {
                    // Hex
                    let original = b85Decode(rawOriginal);
                    let buyback = b85Decode(rawBuyback);

                    let results = affineGapAlignment(original, buyback);

                    if (!(key in stats)) stats[key] = {matches: 0, differences: 0, additions: 0, total: 0};
                    stats[key].matches += results.stats.matches * 4;
                    stats[key].differences += results.stats.differences * 4;
                    stats[key].additions += results.stats.additions * 4;
                    stats[key].total += results.stats.total * 4;
                    // Punish
                    stats[key].matches -= results.stats.differences * 2;
                    stats[key].matches -= results.stats.additions * 2;

                    // Binary
                    let originalBin = hexToBin(original);
                    let buybackBin = hexToBin(buyback);

                    results = affineGapAlignment(originalBin, buybackBin);
                    stats[key].matches += results.stats.matches;
                    stats[key].differences += results.stats.differences;
                    stats[key].additions += results.stats.additions;
                    stats[key].total += results.stats.total;
                    // Punish
                    stats[key].matches -= results.stats.differences;
                    stats[key].matches -= results.stats.additions;
                }
            }
        }
    }
}

// Calculate statistical metrics
function calculateStats(values) {
    const n = values.length;
    const mean = values.reduce((sum, val) => sum + val, 0) / n;
    const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / n;
    const stdDev = Math.sqrt(variance);
    return { mean, stdDev, n };
}

function getZScore(value, mean, stdDev) {
    if (stdDev === 0) return 0;
    return (value - mean) / stdDev;
}

function getConfidenceLevel(zScore) {
    const absZ = Math.abs(zScore);
    if (absZ >= 3.29) return "99.9%";
    if (absZ >= 2.58) return "99%";
    if (absZ >= 1.96) return "95%";
    if (absZ >= 1.65) return "90%";
    return "< 90% (likely noise)";
}

console.log("Byte Order\tMatches\tDifferences\tAdditions\tTotal\t% Matches");
let bestKey = null;
let bestMatches = -1;
let secondBestMatches = -1;
let matchPercentages = [];

for (let key in stats) {
    let s = stats[key];
    let pct = (s.matches / s.total * 100);
    matchPercentages.push({ key, matches: s.matches, pct, stats: s });
    console.log(`${key}\t${s.matches}\t${s.differences}\t${s.additions}\t${s.total}\t${pct.toFixed(2)}%`);

    if (s.matches > bestMatches) {
        secondBestMatches = bestMatches;
        bestMatches = s.matches;
        bestKey = key;
    } else if (s.matches > secondBestMatches) {
        secondBestMatches = s.matches;
    }
}

// Sort by match percentage
matchPercentages.sort((a, b) => b.pct - a.pct);

// Calculate statistical significance
const percentages = matchPercentages.map(m => m.pct);
const matchCounts = matchPercentages.map(m => m.matches);

const pctStats = calculateStats(percentages);
const countStats = calculateStats(matchCounts);

const bestPct = matchPercentages[0].pct;
const secondBestPct = matchPercentages[1].pct;

const zScore = getZScore(bestPct, pctStats.mean, pctStats.stdDev);
const confidenceLevel = getConfidenceLevel(zScore);

console.log();
console.log("=" .repeat(80));
console.log("STATISTICAL ANALYSIS");
console.log("=" .repeat(80));
console.log();

console.log(`Best byte order: ${bestKey} with ${bestMatches} matches (${bestPct.toFixed(2)}%)`);
console.log(`Second best:     ${matchPercentages[1].key} with ${matchPercentages[1].matches} matches (${secondBestPct.toFixed(2)}%)`);
console.log();

console.log("Population Statistics:");
console.log(`  Mean match rate:        ${pctStats.mean.toFixed(2)}%`);
console.log(`  Standard deviation:     ${pctStats.stdDev.toFixed(2)}%`);
console.log(`  Sample size:            ${pctStats.n} byte orders tested`);
console.log();

console.log("Winner Analysis:");
console.log(`  Z-Score:                ${zScore.toFixed(2)} σ (standard deviations from mean)`);
console.log(`  Confidence level:       ${confidenceLevel}`);
console.log(`  Gap to 2nd place:       ${(bestPct - secondBestPct).toFixed(2)}% (${((bestPct - secondBestPct) / pctStats.stdDev).toFixed(2)} σ)`);
console.log(`  Gap to mean:            ${(bestPct - pctStats.mean).toFixed(2)}%`);
console.log();

// Interpretation
console.log("Interpretation:");
if (zScore >= 2.58) {
    console.log(`  ✓ STRONG SIGNAL: The winner is ${zScore.toFixed(2)} standard deviations above the mean.`);
    console.log(`    This is statistically significant at the ${confidenceLevel} confidence level.`);
    console.log(`    This is almost certainly NOT random noise.`);
} else if (zScore >= 1.96) {
    console.log(`  ✓ MODERATE SIGNAL: The winner is ${zScore.toFixed(2)} standard deviations above the mean.`);
    console.log(`    This is statistically significant at the ${confidenceLevel} confidence level.`);
    console.log(`    Likely a true winner, but consider getting more test data.`);
} else if (zScore >= 1.0) {
    console.log(`  ⚠ WEAK SIGNAL: The winner is only ${zScore.toFixed(2)} standard deviations above the mean.`);
    console.log(`    Confidence level: ${confidenceLevel}`);
    console.log(`    This could be noise. Consider collecting more test data.`);
} else {
    console.log(`  ✗ NO SIGNAL: The winner is only ${zScore.toFixed(2)} standard deviations above the mean.`);
    console.log(`    This is likely just random noise. The byte order may not matter.`);
}

console.log();
console.log("Top 5 Results:");
for (let i = 0; i < Math.min(5, matchPercentages.length); i++) {
    const m = matchPercentages[i];
    const z = getZScore(m.pct, pctStats.mean, pctStats.stdDev);
    console.log(`  ${i + 1}. ${m.key}\t${m.pct.toFixed(2)}%\t(z=${z.toFixed(2)})`);
}

/*
Hmm
- I finally managed to get the b85 encoding/decoding to accept arbitrary byte orders
(and succeds rounds trips FFS)
- I bruteforced the byte order of
*/
