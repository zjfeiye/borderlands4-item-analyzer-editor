import {itemDecodeLevel} from "./lib/item_decode_read_level.js";
import {b85Decode} from "./lib/b85.js";
import {hexToBin} from "./lib/hex_to_bin.js";

function level(serial) {
    return itemDecodeLevel(hexToBin(b85Decode(serial)));
}

console.log('Expected: 49', '\t Got:', level('@Ugct)%FmVuJXn{hb3U#POJ!&6nQ*lsxP_0lm5d'));
console.log('Expected: 50', '\t Got:', level('@Ugy3L+2}Ta0Od!H/&7hp9LM3WZH&OXe^H7_bgUW^ag#Z'));
console.log('Expected: 50', '\t Got:', level('@Ugy3L+2}TYg%$yC%i7M2gZldO)@}cgb!l34$a-qf{00'));
console.log('Expected: 50', '\t Got:', level('@Ugy3L+2}Ta0Od!I{*`S=LLLKTRY91;d>K-Z#Y7QzFY8(O'));
console.log('Expected: 13', '\t Got:', level('@UgwSAs38n)gOz#USjp~P5)S(jfsJ*DNsIaI@g+bLpr9!Pj^+J_H00'));
console.log('Expected: -32768', '\t Got:', level('@Ugr$WBm/!4;hzOS?LXR5M`e<&*6{#ej00'));
console.log('Expected: -3', '\t Got:', level('@Ugr$WBm/*(<j/i6}LXR5M`e<&*6{#ej00'));
console.log('Expected: -2', '\t Got:', level('@Ugr$WBm/*<>j/i6}LXR5M`e<&*6{#ej00'));
console.log('Expected: -1', '\t Got:', level('@Ugr$WBm/*_@j/i6}LXR5M`e<&*6{#ej00'));
console.log('Expected: 13', '\t Got:', level('@Ugr%Scm/z+aM(zhas#5K%1KJ%;3J%l='));
