import {b85Decode} from "./lib/b85.js";
import {hexToBin} from "./lib/hex_to_bin.js";
import {smg} from "./res/smg.js";
import {pistols} from "./res/pistols.js";
import randomItems from "./res/randomItems";
import {itemDecodeLevel} from "./lib/item_decode_read_level.js";

let items = [];
items.push(...smg);
items.push(...pistols);
items.push(...);

let totalMatches = 0;
let totalDiffs = 0;

for (let serial of items) {
    // Prepare the data
    let bin = hexToBin(b85Decode(serial));
    let actualMarker = bin.indexOf('00000011001000001100');
    let condition;
    let pos = 0;

    // Finding logic
    {
        pos += 13;

        condition = bin[++pos] === '1';
        pos += condition ? 9 : 0; // 9 conditional bits

        pos += 1; // Static 1 bit

        condition = bin[pos++] === '1';
        pos += condition ? 5 : 0; // 5 conditional bits
    }

    // Store output
    //console.log(actualMarker, pos, serial);
    console.log(bin.slice(0, 50));
    if (actualMarker === pos) totalMatches++;
    else totalDiffs++;
}

console.log('Matches:', totalMatches);
console.log('Fail:', totalDiffs);
