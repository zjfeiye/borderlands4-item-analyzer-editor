import {b85Decode, b85Encode} from './lib/b85.js';
import {hexToInt, intToHex} from './lib/chr_hex.js';

let item = '@UgeU_{Fme!Krh`(W3U#PP4HtS;PE<(LNYtjnpz5Ihp!%R{q0XU(G5`';

console.log('Base item: ', item);
item = b85Decode(item)
console.log('Decoded: ', item);

item = '8060e084220e46092a09e48ca1d42a8d47a8951a43cd43dd6a0caa7d2a172a0e0225aa1c';

console.log('Bitswapping...');
console.log('');

let backpackCounter = 0;
for (let pos = 0; pos < item.length; pos++) {
    for (let bit = 0; bit < 4; bit++) {
        let newItem = item;

        let char = hexToInt(newItem[pos]);
        char ^= (1 << bit);
        newItem = newItem.substring(0, pos) + intToHex(char) + newItem.substring(pos + 1);

        // console.log(newItem);
        console.log('        slot_' + backpackCounter + ':');
        console.log('          serial: \'' + b85Encode(newItem) + '\'');

        backpackCounter++;
    }
}
