import { b85Decode, b85Encode, base85ChangeByteOrder } from './lib/b85.js';

let roundTrips = [
    '8424034c30591061f474505854a17ea27aa2dea062a15222',
    '8424034c305e10616c4e505854a17ea27aa2dea062a15222',
    '8424034c307210617435505854a17ea27aa2dea062a15222',
    '8424034c30591061f474505854a17ea27aa2dea062a15222f0',
    '8424034c305e10616c4e505854a17ea27aa2dea062a15222f0',
    '8424034c307210617435505854a17ea27aa2dea062a15222f0',
    '8424034c30591061f474505854a17ea27aa2dea062a152220f',
    '8424034c305e10616c4e505854a17ea27aa2dea062a152220f',
    '8424034c307210617435505854a17ea27aa2dea062a152220f',
    '8424034c30591061f474505854a17ea27aa2dea062a1522200',
    '8424034c305e10616c4e505854a17ea27aa2dea062a1522200',
    '8424034c307210617435505854a17ea27aa2dea062a1522200',
    'f0b1b79fadf3c5dcfefc4f71f35c1a41ce3615534a2cbe47b5be',
    'f0b1b79fadf3c60a5405d514d735f454ce3615534a2cbe47b5be',
    'f0b1b79fadf3c6bfc1a7ab79ec5e476ece3615534a2cbe47b5be',
    'f0b1b79fadf3c5dcfefc4f71f35c1a41ce3615534a2cbe47b5be0a',
    'f0b1b79fadf3c60a5405d514d735f454ce3615534a2cbe47b5be0a',
    'f0b1b79fadf3c6bfc1a7ab79ec5e476ece3615534a2cbe47b5be0a',
];

// Compute every combination of byte order
let success = 0, fail = 0;
for (let i = 0; i < 4; i++) {
    for (let j = 0; j < 4; j++) {
        for (let k = 0; k < 4; k++) {
            for (let l = 0; l < 4; l++) {
                if (i === j || i === k || i === l || j === k || j === l || k === l)
                    continue;

                base85ChangeByteOrder([i, j, k, l]);
                for (let hex of roundTrips) {
                    let encoded = b85Encode(hex);
                    let decoded = b85Decode(encoded);
                    console.log(`${hex} => ${encoded} => ${decoded} : ${hex === decoded}`);
                    if (hex === decoded) success++; else fail++;
                }
            }
        }
    }
}

console.log(`Success: ${success}, Fail: ${fail}`);
if (fail === 0) {
    console.log("All tests passed!");
} else {
    console.log("Some tests failed.");
}

base85ChangeByteOrder([0, 1, 2, 3]);
console.log(b85Encode('aef0c94fa2caf699'))
