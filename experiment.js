import {b85Decode, b85Encode} from "./lib/b85.js";

let backpackCounter = 0;
let backpackAccumulator = '';
function backpack(hex) {
    let encoded = b85Encode(hex);
    hex = hex.replaceAll(' ', '')
    backpackAccumulator += '        slot_' + backpackCounter + ':' + '\n';
    backpackAccumulator += '          serial: \'' + encoded + '\'' + '\n';
    backpackCounter++;
    return encoded;
}

console.log('PURPLE: ', b85Decode(''))
console.log('BLUE:   ', b85Decode(''))
console.log('GREEN:  ', b85Decode(''))

console.log('JAKOBS WHITE 1:  ', b85Decode('@Ugy3L+2}TYgOveWLiz-y4Hnj&;3v~_w'))
console.log('JAKOBS WHITE 2:  ', b85Decode('@Ugy3L+2}TYgjKu@`iz-y4I#maC3snvQ'))
console.log('NORMAL TRUCK 1:  ', b85Decode('@Ugy3L+2}TYg%-;pdi7Hg15_J<b4^<D<sXeGvs9UIV2m'))
console.log('PEARL TRUCK:     ', b85Decode('@Ugy3L+2}TYg49*P7i7Hg1Zldy`>Y?VLI#mbN2UQDo4)HKHKL7'))




console.log('WHITE:  ', b85Decode('@UgwSAs2}TYg41^5&i/U73)T25z2bBx84mA$}'))

console.log()
console.log()
console.log()
console.log()
console.log('ORIGINAL :     ', b85Decode('@UgxFw!2}TYg%-slziz?Kj67?1p7WJu@s5z)Us8*<5sB@@zsC@_'))
console.log('GRIP VARIANT:  ', b85Decode('@UgxFw!2}TYg%-slziz?Kj67?1p7WJu@s5z)Us8*<1sB@@zsC@_'))
console.log('SCOPE VARIANT: ', b85Decode('@UgxFw!2}TYg%-slziz?Kj67?1p7WJu@s5z)Ss8*<5sB@@zsC@_'))
console.log('NO GYROJET:    ', b85Decode('@UgxFw!2}TYg%-slziz?Kj67?1p7WJvOs5z)Us8*<5sB@@zsC@_'))
console.log('EXPLODE:       ', b85Decode('@UgxFw!2}TYg%-slziz?Kj64e$J7WJvOs5z)Us8*<5sB@@zsC@_'))
console.log()
console.log()
console.log()
console.log('Wombo combo rifle:')
console.log('FIRE:            ', b85Decode('@Ugvelk2}TYgOoB$D3U#PO4H*iFnu!X7x`R4}Duv30s)u+On@a!'))
console.log('SHOCK:           ', b85Decode('@Ugvelk2}TYgOoB$D3U#PO4IK)Jnu!X7x`R4}Duv30s)u+On@a!'))
console.log('CORROSIVE:       ', b85Decode('@Ugvelk2}TYgOoB$D3U#PO4HXKBiirw?x`R4}Duv30s)u+On@a!'))
// console.log('CRYO:       ', b85Decode('@Ugvelk2}TYgOoB$D3U#PO4HpWDnu!X7x`R4}Duv30s)u+On@a!'))
console.log()
console.log('Scraping convergence shotgun:')
console.log('FIRE:            ', b85Decode('@Ugd77*Fme!Kx;Id2RG/*ls6-7J3W;ios)_nk9@HsRDpW1hF9Z'))
console.log('SHOCK:           ', b85Decode('@Ugd77*Fme!Kx;Id2RG/*ls6-7N3W;ios)_nk9@HsRDpW1hF9Z'))
console.log('CORROSIVE:       ', b85Decode('@Ugd77*Fme!Kx;Id2RG/*ls6-7F3W;ios)_nk9@HsRDpW1hF9Z'))
// console.log('RADIATION:       ', b85Decode('@Ugd77*Fme!Kx;Id2RG/*ls6-7L3W;ios)_nk9@HsRDpW1hF9Z'))
console.log()
console.log()
console.log()
console.log()

console.log("Cryo/corrosive: ", b85Decode('@UgeU_{Fme!Krh`(W3U#PP4HtS;PE<(LNYtjnpz5Ihp!%R{q0XU(H~;'))
console.log("Cryo/radiation: ", b85Decode('@UgeU_{Fme!Krh`(W3U#PP4HtS;PE<(LNYtjnpz5Ihp!%R{q0XU(HUI'))


console.log("[White] Unseen Xiuhcoatl   ", b85Encode("8060e084220e4609fa0ce54ca1d42a8b39a9b52272a85ca808"));
console.log("GPT                        ", b85Encode("8060e084220e4609fa0df8cca1d42a8b39a9b52272a85ca808"));
console.log("GPT                        ", b85Encode("8060e084220e4609fa0df8cca1d42a8b39a9b52272a85ca808"));

console.log("MERGED                     ", b85Encode("8060e084220e4609fa0ce54ca1d42a8b39a9b52272a85ca808"));



console.log("MERGED                     ", b85Encode("8060e084220a4609fa05df8ca1d42a8b7da9151a41e84da842"));

console.log("MERGED                     ", b85Encode("8060e084220a4609fa05df8ca1d42a8b7da9151a41e84da842"));
console.log("MERGED                     ", b85Encode("8060e084220a4609fa05df8ca1d42a8b7da9151a41e84da842" + "d54285954300"));

console.log("[Green] Unseen Xiuhcoatl   ", b85Encode("8060e084220a46090a05df8ca1d42a8d7da9151a41e54da842d54285954300"));
console.log("3 CHANGE                   ", b85Encode("8060e084220a4609fa05df8ca1d42a8b7da9151a41e84da842d54285954300"));
console.log("3 CHANGE + SHORTENED       ", b85Encode("8060e084220a4609fa05df8ca1d42a8b7da9151a41e84da842"));

console.log("GPT                  ", b85Encode("8060e084220e46090a05df8ca1d42a8d7da9151a41e54da841d54285954300"));
console.log("GPT                  ", b85Encode("8060e084220e46090a05df8ca1d42a8d7da9151a41e54da843d54285954300"));
console.log("GPT                  ", b85Encode("8060e084220e46090a05df8ca1d42a8d7da9151a41e54da840d54285954300"));
console.log("GPT                  ", b85Encode("8060e084220e46090a05df8ca1d42a8d7da9151a41e54da844d54285954300"));




console.log("                  ", b85Decode("@Ugy3L+2}TYg4BQJUjVjck61AvE^+Sb3b!rc)7U~=V"));
console.log("                  ", b85Decode("@Ugy3L+2}TYg4BQJUjVjck61AvE^+Sb3b?OeP7U~=V"));


console.log("VANILLA  Top Square Simple:    ", b85Encode("8060e084220e4609fa0ce54ca1d42a8b39a9b52272a85ca808"));
console.log("BITSWAP  Side Long Smooth:     ", b85Encode("8060e084220e4609fa0ce54ca1d42a8b3da9b52272a85ca808"));
console.log("BITSWAP  Round Square Clear:   ", b85Encode("8060e084220e4609fa0ce54ca1d42a8b3ba9b52272a85ca808"));

console.log("VANILLA  Top Square Simple:    ", b85Encode("8060e084220e4609ca0cd78ca2542a8995137516b50f350f5ca839a9a85f08"));
console.log("BITSWAP  Side Long Smooth:     ", b85Encode("8060e084220e4609ca0cd78ca2542a8995137516b50f350f5ca83da9a85f08"));
console.log("BITSWAP  Round Square Clear:   ", b85Encode("8060e084220e4609ca0cd78ca2542a8995137516b50f350f5ca83ba9a85f08"));

console.log("VANILLA  Top Square Simple:    ", b85Encode("8060e084220e46092a0bdc0ca1d42a8d48a8b512448543f5aa0e6a75021cea16"));
console.log("BITSWAP  Side Long Smooth:     ", b85Encode("8060e084220e46092a0bdc0ca1d42a8d48a8b512448543f5aa0f6a75021cea16"));
console.log("BITSWAP  Round Square Clear:   ", b85Encode("8060e084220e46092a0bdc0ca1d42a8d48a8b512448543f5aa0eea75021cea16"));


console.log("VANILLA  Top Square Simple:    ", b85Decode("@Ugy3L+2}TYgOyvyviz?KiBDJYGs9dOW2m"));
console.log("BITSWAP  Side Long Smooth:     ", b85Decode("@Ugy3L+2}TYgOyvyviz?KiBDJYKs9dOW2m"));
console.log("BITSWAP  Round Square Clear:   ", b85Decode("@Ugy3L+2}TYgOyvyviz?KiBDJYIs9dOW2m"));
console.log();
console.log("VANILLA  Top Square Simple:    ", b85Decode("@Ugy3L+2}TYgjMogxi7Hg07IhPq4>b?9sX3@zs9y*"));
console.log("BITSWAP  Side Long Smooth:     ", b85Decode("@Ugy3L+2}TYgjMogxi7Hg07IhPq4>b?9sXeG%s9y*"));
console.log("BITSWAP  Round Square Clear:   ", b85Decode("@Ugy3L+2}TYgjMogxi7Hg07IhPq4>b?9sXM4#s9y*"));
console.log();
console.log("VANILLA  Top Square Simple:    ", b85Decode("@Ugy3L+2}TYg4BQJUjVjck61AvE^+Sb3b!rZ(7U~=V"));
console.log("BITSWAP  Side Long Smooth:     ", b85Decode("@Ugy3L+2}TYg4BQJUjVjck61AvE^+Sb3b!rc)7U~=V"));
console.log("BITSWAP  Round Square Clear:   ", b85Decode("@Ugy3L+2}TYg4BQJUjVjck61AvE^+Sb3b?OeP7U~=V"));
console.log("BITSWAP  Round Square Clear:   ", b85Encode("4c03248461107230585074f4a27ea154a0dea27a2252a16200"));


console.log("1:   ", b85Decode("@Ugg66CFme!K<b6;oRH0s>&Y{+!(xE1G7BvS/3w06!"));
console.log("1:   ", b85Decode("@Ugg66CFme!K<b6;oRH0s>&Y{+!(xE1G7BvS/"));

console.log();
console.log();
console.log();
console.log(backpackAccumulator);
