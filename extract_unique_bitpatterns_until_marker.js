import random from './bl4-serial-matches.js';
import {hexToBin} from "./lib/hex_to_bin.js";
import {b85Decode} from "./lib/b85.js";

let uniquePatterns = {};

for (let item of random) {
    let serial = item.partString;

    if (serial.startsWith('\\"@U')) serial = serial.slice(2);
    if (serial.startsWith('"@U')) serial = serial.slice(1);
    if (serial.endsWith('",')) serial = serial.slice(0, -1);
    if (serial.endsWith('"')) serial = serial.slice(0, -1);
    // if (!serial) continue;

    let b85 = b85Decode(serial);
    if (!b85) continue;
    let bin = hexToBin(b85);
    let actualMarker = bin.indexOf('00000011001000001100');

    if (actualMarker === -1) continue;

    let pattern = bin.slice(0, actualMarker);

    uniquePatterns[pattern] = actualMarker;
}

console.log('Unique patterns found:', Object.keys(uniquePatterns).length);
for (let pattern in uniquePatterns) {
    console.log(`Pattern (length ${uniquePatterns[pattern]}): ${pattern}`);
}
