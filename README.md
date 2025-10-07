title: "Extract Raw Data from Base85 serials theory"
source: "https://bookstack.nicnl.com/books/borderlands-4-item-serials/page/item-level"
author:
published:
created: 2025-10-06
description: "Description of how the levels are encoded in the binary stream.1. Layout:1.1. Find the positio..."
tags:
  - "clippings"
---
# Extract raw data from base85 serials

Description of Borderlands 4's serials strings + a guide of how to extract the underlying data.

### 1. Introduction:

The serials of Borderlands 4's items are seemingly random strings of characters, example:

```
Common Unseen Xiuhcoatl:
@Ugy3L+2}TYgOyvyviz?KiBDJYGs9dOW2m

Green Unseen Xiuhcoatl:
@Ugy3L+2}TMcjNb(cjVjck8WpL1s7>WTg+kRrl/uj

Ambushing Truck:
@Ugy3L+2}TYgjMogxi7Hg07IhPq4>b?9sX3@zs9y*
```

TLDR: Those "serials" are mostly base85 with special tricks.  
Probably encoded in a way to hide or compress the underlying data.

**Warning:**  
A group of 4 bytes are represented using 5 base85 chars.  
Studying those serials in their raw form is a **very bad idea**:  
Any change in any of those 4 bytes is going to **WILDLY** change the resulting base85 serial, making raw analysis unpredictable :  
Bit alignment and tiny changes results in totally different base85 serials, despite the underlying data being 95% the same.  
  
You (and your LLM) will think there are multiple encoding structure formats.  
This is wrong, this is a sideeffect of working with raw base85.

=> No doubt about it : we NEED to transform the base85 serials into usable hexadecimal/bitstream.

### 2. Transformation steps:

After many trial and error, here is out best guess.  
  
We think the game transforms the raw data with multiple steps:

1. The game serializes the item into bytes, this is the underlying data we want to collect.
2. Each individual bytes are mirrored: the bit order goes from `76543210` to `01234567`  
      Example:  a byte of value `10100001` is mirrored into `10000101`
3. The bytes are transformed to big-endian base85 using a custom alphabet:  
    ``0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~``  
    
4. The prefix `@U` is added to the start of the base85 string.

Symmetrically, we can extract the raw data behind the serials by doing this steps in reverse:

1. Remove the prefix @U at the beginning of the serial.
2. Transform this base85 string into bytes using the custom alphabet. (Don't forget: big-endian)
3. Mirror each bytes.
4. We now have the raw data ready for analysis and alterations!

Here is the link for a python implementation of the decoding from a full serial to binary bitstream:  
[https://gitlab.nicnl.com/Nicnl/borderlands_4_item_tinker/-/blob/5b33bbbf73c90c387e239394d86279d2aa6ff2c1/borderlands_4_base85_decoder.py](https://gitlab.nicnl.com/Nicnl/borderlands_4_item_tinker/-/blob/5b33bbbf73c90c387e239394d86279d2aa6ff2c1/borderlands_4_base85_decoder.py)  

The encoding is not yet available in python format.  
However the online webtool is available at this link: [https://borderlands4-serial-comparator.nicnl.com/](https://borderlands4-serial-comparator.nicnl.com/)  
This tool will transform serials between base85 and its binary bitstream.  
The decoding matches what is being done in the python script, feel free to insert serials and compare results.

### 3. Example:

Below is an example with an actual item:

```
Item:
  Jakobs Sniper
  Purple Looming Inkanyamba

Raw serial:
  @Ugy3L+2}TYgj66_jRG}7?s7KX9%/mS}4=NOD6e<_$90C

Step 1: strip the '@U' prefix:
  y3L+2}TYgj66_jRG}7?s7KX9%/mS}4=NOD6e<_$90C

Step 2: convert from base85 to hex (using custom alphabet + big endian)
  As hex: 84e0608009460e228c3c506954a11695a847d543cd436d2a0f2a146a142a17ea1c02
  As bin: 10000100111000000110000010000000000010010100011000001110001000101000110000111100010100000110100101010100101000010001011010010101101010000100011111010101010000111100110101000011011011010010101000001111001010100001010001101010000101000010101000010111111010100001110000000010

Step 3: mirror each bytes
  As hex: 2107060190627044313c0a962a8568a915e2abc2b3c2b654f05428562854e8573840
  As bin: 00100001000001110000011000000001100100000110001001110000010001000011000100111100000010101001011000101010100001010110100010101001000101011110001010101011110000101011001111000010101101100101010011110000010101000010100001010110001010000101010011101000010101110011100001000000
```

### 4. Fact checking:

Is this correct or not?

We figured this out thanks to a special phenomenon we call "buyback".  
Basically, selling a **looted** item to a vending machine and buying it back **changes the serial**.  
The serial gets longer, but most importantly it gets scrambled up!  

Below are a few example of this phenomenon:

```
L50 Legendary Cooking Ambushing Truck
  Original: @Ugy3L+2}TYg%$yC%i7M2gZldO)@}cgb!l34$a-qf{00
  Buyback:  @Ugy3L+2}Ta0Od!I{*`S=LLLKTRY91;d>K-Z#Y7QzFY8(O

L50 Common Unseen Xiuhcoatl
  Original: @Ugy3L+2}TYgOyvyviz?KiBDJYGs9dOW2m
  Buyback:  @Ugy3L+2}Ta0Od!Hk&Y-`jLLDkno0@~lg(`;t

L49 Common Thrown Quality-Assured Widget
  Original: @UgcJizFmVuJFlEqRRG}I*bSP4ldV~6d`h_Zs00
  Buyback:  @UgcJizFmVuN0ucsN2K_}9s!>CSB2}q3s6VJ*sImw
```

Knowing that base85 is heavily affected by tiny changes, we used those item pairs as a Rosetta Stone for figuring out the encoding.

Below are comparisons of hexadecimal representation of this item using different decoding parameters.

```
L50 Legendary Cooking Ambushing Truck
  Original: @Ugy3L+2}TYg%$yC%i7M2gZldO)@}cgb!l34$a-qf{00
  Buyback:  @Ugy3L+2}Ta0Od!I{*`S=LLLKTRY91;d>K-Z#Y7QzFY8(O
  Match:    ==========!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!++
```

Those two serials looks completely different, despite being the **exact same** item.  
As you will see below, only one combinations is able to align and match those two completely : big-endian + bit-mirror.

Note: the actual hex content is not the important part. What matters is how good those items match.  
Despite the serials being different they were KNOWN identical items, meaning the underlying data HAD to be very similar.  
This is what we aimed for: we adjusted our decoding until both the original and the buyback items matched.

#### Little-endian + no bit-mirror:

[[833046dd5aa38d7b9e2768e9623cf465_MD5.jpeg|Open: Pasted image 20251006224622.png]]
![[833046dd5aa38d7b9e2768e9623cf465_MD5.jpeg]]```


```
Original: 8060e084220e460           9ca0d9ccca1d42a89a1e6a26ea1eea1f2a0e6a0c221c6a17200
Buyback:  8060e084a20e4609ccc2204ca89ca0d926ea1d421f2a1e6a0c2a1eea172a0e6a      6a1 c02
Diff:     ========!======+++++++++++======!!!=====!!!=====!!!======!======++++++===+!=!
Overall - Match: 60% / Diff: 17% / Added: 23%
```

#### Little-endian + bit-mirror:

[![[da6cd04363fcf496731bbc5f124bb7ed_MD5.png]]](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/eXuimage.png)

```
Original: 010607214470629053b03933852b5491856745768577854f056705438463854e0       0
Buyback:  0106072145706290   334304321539059b6457b842f854785630547857e8547056563840
Diff:     =========!======+++!=!=!!!=!=!=!!!!!===!=!!!===!!==!===!=!!!===!=+++++++=
Overall - Match: 52% / Diff: 34% / Added: 14%
```

#### Big-endian + no bit-mirror:

[![[57420fb7c0bacfea52f78d6abedfe45b_MD5.png]]](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/tFXimage.png)

```
Original: 84e0608009460e   22cc9c0dca892ad4a16ea2e6a1f2a1eea1c2a0e6a072a1c621 00
Buyback:  84e0608009460ea24c20c2ccd9a09ca8421dea266a1e2a1fea1e2a0c6a0e2a176a1c02
Diff:     ==============+++!=!=!=!=!=!=!=!=!=!===!===!===!===!===!===!===!=!=+=!
Overall - Match: 67% / Diff: 27% / Added: 6%
```

#### Big-endian + bit-mirror:

[![[17ee68ef4156f624884c145ec4fdff94_MD5.png]]](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/ooLimage.png)

```
Original: 2107060190627     0443339b05391542b85764567854f857785430567054e85638400
Buyback:  2107060190627045320443339b05391542b85764567854f857785430567054e856384 0
Diff:     =============+++++===================================================+=
Overall - Match: 92% / Diff: 0% / Added: 8%
```

### 5. Round Trip:

Current implementation DOES survive all round trips thrown at it.  
( Aka: decode, encode, re-decode, everything should stay the same. )

We used serials obtained from the game + forged/fuzzed hex data just in case.

Implementation available here:  
[https://gitlab.nicnl.com/Nicnl/borderlands_4_item_tinker/-/blob/15dc834e5daf3a32d275a9335fcaaa05d4902038/lib/b85.js](https://gitlab.nicnl.com/Nicnl/borderlands_4_item_tinker/-/blob/15dc834e5daf3a32d275a9335fcaaa05d4902038/lib/b85.js)  
  
Unit tests available here:  
[https://gitlab.nicnl.com/Nicnl/borderlands_4_item_tinker/-/blob/15dc834e5daf3a32d275a9335fcaaa05d4902038/unit_test.js](https://gitlab.nicnl.com/Nicnl/borderlands_4_item_tinker/-/blob/15dc834e5daf3a32d275a9335fcaaa05d4902038/unit_test.js)  

### 6. Credits

@Sparkie for his initial base85 implementation + his alphabet  
@InflamedSebi for his the bit-mirror breakthrough  
@Nicnl for additional work and webtool

====

# Item Level analyzing and editing (Very sought out feature I would so love to have):

https://github.com/hum4nature/borderlands4-item-analyzer-editor/blob/main/READ%20ME%20Item%20Level.docx

https://bookstack.nicnl.com/books/borderlands-4-item-serials/page/item-level




Stuff to investigate:

Modified Header:

1) I had a modded item
=> high dps level 50 illegal weapon
2) Action: I modified it to level 1
3) Result: a big part of the header INCLUDING the "marker" for the level bits HAS DISAPPEARED!

Research to do: where are the level bits now?


Reminder: level bits "marker" we use is "00000011001000001100"


Original
Level 50:        @UgeU_{Fme!KvVPE@CK{7XA`1W
                 00100001000101001100 0000001 1001000001100 01001 11000 001000100001100100110101111110000010110000010101100100010110001100100110110010010001001101000000000000
                                      ^^^^^^^ ^^^^^^^^^^^^^ LLLLc LLLLc
                                      marker


Forged
Level 1:         @UgeU_{Fme!KvVPE@CK{7XA`1W
                 00100001000101001100 0000001 1001000001100 10000        001000100001100100110101111110000010110000010101100100010110001100100110110010010001001101000000000
                                      ^^^^^^^ ^^^^^^^^^^^^^ LLLLc
                                      marker


Going in-game:   @UgeU`yFj+rnP!o;GCXodI
Level 1          00100001000101001100 0000001                             10001000011001001101011111100000101100000101011001000101100011001001101100100100010011010000000000000
                 ==================== =======------------- -----        --==================================================================================================---
                                      ?????????????????????????????????????
                                           WHERE ARE THE LEVEL BITS NOW???


UPDATE: I tried to bitswap the "levelless" item.........
I COULD NOT BITSWAP IT TO ANY OTHER LEVEL
........ wtf
have I created a level-less item???

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

im dumping everytime the convos in my cursor he interprets it and that E1 i told my ai dont focus on tht bl parts need to be compatible you cant just install anything on any gun mostly brand locked
it asked to make a script to detect the parts and tommorow ill test the script to see if he can pinpoint every gun parts on the blocks 
@Mattmab
the end script should tell me all part detected on a seed
im using the docu from @Nicnl
that he meticulously document
Ah! That's a crucial insight! You're saying that the 2-3 character sections we've been finding (like mzS59, sCuY(, dZ>3h) are actually part of a whole - they're components that make up many parts together.
So instead of thinking:
mzS59 = 1 barrel part
sCuY( = 1 stock part
dZ>3h = 1 magazine part
It's more like:
Multiple 2-3 character sections combine to form 1 complete barrel
Multiple 2-3 character sections combine to form 1 complete stock
Multiple 2-3 character sections combine to form 1 complete magazine
This explains why:
Our single pattern insertions aren't working properly
We need multiple related patterns to form complete parts
The working modded seeds probably have complete part sets
We're inserting incomplete parts that cause malus
So we need to:
Identify complete part sets (multiple related patterns)
Insert entire part sets instead of individual patterns
Study the working modded seeds to see their complete part combinations
Understand the part structure better
This is a much more complex system than we initially thought! Should I create a system that analyzes complete part sets instead of individual patterns?
-
exactly white
when taken down to hex and binary and put in the right order parts can be sort of read. but hard to determine exactly whats going on right now. more research is needed.
yeah i see he just wrote  an seed analyzer to chk that
-
Key Findings:
Working Seed 1 has 3 complete parts:
2 stock parts (155e15ee) at positions 8 and 12
1 barrel part (e9e9e9e9) at position 32
Pattern Relationships:
Barrel patterns: mzS, S59, Pmz, 9mz - these are the 2-3 character components
Stock patterns: sCu, CuY, EsC - these combine to form complete stock parts




