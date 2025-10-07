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




============================

Description of how the levels are encoded in the binary stream.

### 1\. Layout:

##### 1.1. Find the position of the level-bits:

The bits governing the level are positioned seemingly randomly, see below:

\=============================================LLLLc==============

\=================================================LLLLcLLLLc=====

\========================================LLLLcLLLLc==============

We have not figured out how the header decodes, so positioning the level bits is tricky.  
However, there is a workaround: the levels bits seems always positioned after a specific bit pattern: `00000011001000001100`  
The level bits are always positioned after this marker.  

marker

vvvvvvvvvvvvvvvvvvvv

\=========================00000011001000001100LLLLcLLLLc=========

^^^^^

level bits

##### 1.2. Read the varint:

The level bits are encoded in a very weird format: varints.  
Even worse: 5 bits varints, between 1 and 4 blocks.  
Those terms are complicated, here is a quick walkthrough:

Varints are a way to store integers over a varying number of blocks, depending on the size of the integer.  
Small integers will take only one block, other two, and others three, etc...

They're encoded as follow:  
  

data

vvvv

DDDDc

^

continuation bit

Here are a few examples:

stop

v

10100

^^^^

data

  

\- Raw data is: 1010

\- Mirrored: 0101

\- To decimal: 5

continue stop here

v v

10101 00100

^^^^ ^^^^

data data

  

\- Raw data is: 10100010

\- Mirrored: 01000101

\- To decimal: 69

continue continue continue stop

v v v v

11111 11111 11111 11110

^^^^ ^^^^ ^^^^ ^^^^

data data data data

  

\- Raw data is: 1111111111111111

\- Mirrored: 1111111111111111

\- To decimal: -32768

stop

v

00000

^^^^

data

  

\- Raw data is: 0000

\- Mirrored: 0000

\- To decimal: 0

continue stop

v v

00001 00000

^^^^ ^^^^

data data

  

\- Raw data is: 00000000

\- Mirrored: 00000000

\- To decimal: 0

Note: there are multiple ways to encode the integer zero.  
The game will reserialize (collapse) the item back to the shortest one-block representation.  

\=> Just apply this logic to the bits after the marker, and you'll extract the item level.

### 2\. Examples:

Below are a few examples of how to decode the level of actual existing items.

Step 1:

Raw serial: @Ugr$xKm/)}}$pj({\_X>Jcq0UExO{SqiosR~Z6aW

  

  

Step 2: extract the first bits using the webtool:

00100001101001010111000101100000000110010000011000100111000001001001001100100000010

  

  

Step 3: workaround for finding the level bits, search for this string: 00000011001000001100

Found here:

00100001101001010111000101100000000110010000011000100111000001001001001100100000010

^^^^^^^^^^^^^^^^^^^^

  

  

Step 4: the level bits are right after the marker

00100001101001010111000101100000000110010000011000100111000001001001001100100000010

\--------------------LLLLc

continuation bit=1, we must read 5 more bits -|

  

  

Step 5: continuation bit was 1, we must continue

00100001101001010111000101100000000110010000011000100111000001001001001100100000010

\-------------------------LLLLc

continuation bit=0, we done reading -|

  

  

Step 4: assemble the data

LLLLc LLLc: 01001 11000

  

Step 5: discard the continuation bit, we don't need them anymore

LLLL LLLL: 0100 1100

  

Step 6: reverse the string:

01001100 => 00110010

  

Step 7: binary to decimal

00110010 => 50

  

\=> Item is level 50

serial: @Ugd77\*Fg\_4rx=zp;RG}I\*T&N7HBq}9pC29=n4yqJt7iug5

  

search marker: 00000011001000001100

  

found here

vvvvvvvvvvvvvvvvvvvv

0010000100111000110000000011001000001100 01111 100000010001000011001011101....

LLLLc LLLLc

level bits: 01111 10000

discard continuation bit: 0111 1000

  

extracted: 01111000

reverse: 00011110

to decimal: 30

\=> Item is level 30

Using this method, we have been able to take an existing serial, and forge all items from level 1 to level 50:  

Item: Killshot Vivisecting Throwing Knife

Level 1: @Ugr$WBm/!9x!X=5&qXxA;nj3OOD#<4R

Level 2: @Ugr$WBm/!Fz!X=5&qXxA;nj3OOD#<4R

Level 3: @Ugr$WBm/!L#!X=5&qXxA;nj3OOD#<4R

Level 4: @Ugr$WBm/!R%!X=5&qXxA;nj3OOD#<4R

Level 5: @Ugr$WBm/!X(!X=5&qXxA;nj3OOD#<4R

Level 6: @Ugr$WBm/!d\*!X=5&qXxA;nj3OOD#<4R

Level 7: @Ugr$WBm/!j-!X=5&qXxA;nj3OOD#<4R

Level 8: @Ugr$WBm/!p<!X=5&qXxA;nj3OOD#<4R

Level 9: @Ugr$WBm/!v>!X=5&qXxA;nj3OOD#<4R

Level 10: @Ugr$WBm/!#@!X=5&qXxA;nj3OOD#<4R

Level 11: @Ugr$WBm/!\*\_!X=5&qXxA;nj3OOD#<4R

Level 12: @Ugr$WBm/!>{!X=5&qXxA;nj3OOD#<4R

Level 13: @Ugr$WBm/!{}!X=5&qXxA;nj3OOD#<4R

Level 14: @Ugr$WBm/#30!X=5&qXxA;nj3OOD#<4R

Level 15: @Ugr$WBm/#92!X=5&qXxA;nj3OOD#<4R

Level 16: @Ugr$WBm/$Qa!X=5&qXxA;nj3OOD#<4R

Level 17: @Ugr$WBm/$Wc!X=5&qXxA;nj3OOD#<4R

Level 18: @Ugr$WBm/$ce!X=5&qXxA;nj3OOD#<4R

Level 19: @Ugr$WBm/$ig!X=5&qXxA;nj3OOD#<4R

Level 20: @Ugr$WBm/$oi!X=5&qXxA;nj3OOD#<4R

Level 21: @Ugr$WBm/$uk!X=5&qXxA;nj3OOD#<4R

Level 22: @Ugr$WBm/$!m!X=5&qXxA;nj3OOD#<4R

Level 23: @Ugr$WBm/$)o!X=5&qXxA;nj3OOD#<4R

Level 24: @Ugr$WBm/$=q!X=5&qXxA;nj3OOD#<4R

Level 25: @Ugr$WBm/$\`s!X=5&qXxA;nj3OOD#<4R

Level 26: @Ugr$WBm/%1u!X=5&qXxA;nj3OOD#<4R

Level 27: @Ugr$WBm/%7w!X=5&qXxA;nj3OOD#<4R

Level 28: @Ugr$WBm/%Dy!X=5&qXxA;nj3OOD#<4R

Level 29: @Ugr$WBm/%J!!X=5&qXxA;nj3OOD#<4R

Level 30: @Ugr$WBm/%P$!X=5&qXxA;nj3OOD#<4R

Level 31: @Ugr$WBm/%V&!X=5&qXxA;nj3OOD#<4R

Level 32: @Ugr$WBm/&nF!X=5&qXxA;nj3OOD#<4R

Level 33: @Ugr$WBm/&tH!X=5&qXxA;nj3OOD#<4R

Level 34: @Ugr$WBm/&zJ!X=5&qXxA;nj3OOD#<4R

Level 35: @Ugr$WBm/&(L!X=5&qXxA;nj3OOD#<4R

Level 36: @Ugr$WBm/&<N!X=5&qXxA;nj3OOD#<4R

Level 37: @Ugr$WBm/&\_P!X=5&qXxA;nj3OOD#<4R

Level 38: @Ugr$WBm/(0R!X=5&qXxA;nj3OOD#<4R

Level 39: @Ugr$WBm/(6T!X=5&qXxA;nj3OOD#<4R

Level 40: @Ugr$WBm/(CV!X=5&qXxA;nj3OOD#<4R

Level 41: @Ugr$WBm/(IX!X=5&qXxA;nj3OOD#<4R

Level 42: @Ugr$WBm/(OZ!X=5&qXxA;nj3OOD#<4R

Level 43: @Ugr$WBm/(Ub!X=5&qXxA;nj3OOD#<4R

Level 44: @Ugr$WBm/(ad!X=5&qXxA;nj3OOD#<4R

Level 45: @Ugr$WBm/(gf!X=5&qXxA;nj3OOD#<4R

Level 46: @Ugr$WBm/(mh!X=5&qXxA;nj3OOD#<4R

Level 47: @Ugr$WBm/(sj!X=5&qXxA;nj3OOD#<4R

Level 48: @Ugr$WBm/)-\_!X=5&qXxA;nj3OOD#<4R

Level 49: @Ugr$WBm/)@{!X=5&qXxA;nj3OOD#<4R

Level 50: @Ugr$WBm/)}}!X=5&qXxA;nj3OOD#<4R

  

Note: those items between level 1 and 15 have the redundant zero-value varint mentioned.

Those items are going to get reserialized/collapsed to a shorter serial when loading in-game.

We were also able to generate "unholy" serials:

Level 64: @Ugr$WBm/!4<fC!f)LXR5M\`e<&\*6{#ej00

Note: did not spawn, game probably have a hardcoded limit.

  

Level 0: @Ugr$WBm/!4;fC!f)LXR5M\`e<&\*6{#ej00

Note: did spawn in-game, no level shown on screen, and had less damage than its level 1 counterpart.

  

Level -3: @Ugr$WBm/\*(<j/i6}LXR5M\`e<&\*6{#ej00

Note: did spawn in game, shown as level negative 3, and had even less damage than the level 0 and 1 combined.

  

Minimum value of int16: @Ugr$WBm/!4;hzOS?LXR5M\`e<&\*6{#ej00

Note: DID SPAWN AS LEVEL -32768. THIS IS FUCKING UNHOLY.

(See screenshot below)

[![[d8777b2e19eade12dc82df82f7c90e7f_MD5.png]]](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/LV1image.png)

### 3\. Discovery:

How did we discover this?

We performed bitswapping on existing weapons to create variant with different levels.  
We noticed that the bits governing the levels were not aligned:

\=============================================!!!!1!!000=========

\=================================================!!!!1!!000=====

\========================================!!!!1!!000==============

We didn't know why.  
However we noticed two things:

1. There was a floating "1" in the middle of the level bits, suggesting varint fuckery.
2. A bitswapped level 3 item got reserialized to a shorter serial.

Those to elements were our Rosetta stone for understanding how this 5-bit varint worked.

altered level bits

vvvv vv

0010000110100101101000010110000000011001000001100 1100 1 00000 00100010... 10000 000

0010000110100101101000010110000000011001000001100 1100 0 00100010... 10000

\================================================= ====! ----- ========... ===== ---

/ \\ \\ padding removed so is multiple of 8 bits

/ \\

"floating bit" set to zero -/ \\- block of 5 bits removed

### 4\. Credits:

@Nicnl for understanding the 5-bit varint logic.



