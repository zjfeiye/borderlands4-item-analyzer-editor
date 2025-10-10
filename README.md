# Borderlands 4: Item Serials

# First steps: base85 and data types

# Convert raw serial to bitstream

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
Studying those serials in their raw form is a <span style="color: rgb(224, 62, 45);">**very bad idea**</span>:  
Any change in any of those 4 bytes is going to <span style="text-decoration: underline;">**WILDLY**</span> change the resulting base85 serial, making raw analysis unpredictable :  
Bit alignment and tiny changes results in totally different base85 serials, despite the underlying data being 95% the same.  
  
You (and your LLM) will think there are multiple encoding structure formats.  
This is wrong, this is a sideeffect of working with raw base85.

=&gt; No doubt about it : we NEED to transform the base85 serials into usable hexadecimal/bitstream.

### 2. Transformation steps:

After many trial and error, here is out best guess.  
  
We think the game transforms the raw data with multiple steps:

1. The game serializes the item into bytes, this is the underlying data we want to collect.
2. Each individual bytes are mirrored: the bit order goes from `76543210` to `01234567`  
     Example: a byte of value `10100001` is mirrored into `10000101`
3. The bytes are transformed to big-endian base85 using a custom alphabet:  
    `0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~`
4. The prefix `@U` is added to the start of the base85 string.

Symmetrically, we can extract the raw data behind the serials by doing this steps in reverse:

1. Remove the prefix @U at the beginning of the serial.
2. Transform this base85 string into bytes using the custom alphabet. (Don't forget: big-endian)
3. Mirror each bytes.
4. We now have the raw data ready for analysis and alterations!

Here is the link for a python implementation of the decoding from a full serial to binary bitstream:  
[https://gitlab.nicnl.com/Nicnl/borderlands\_4\_item\_tinker/-/blob/5b33bbbf73c90c387e239394d86279d2aa6ff2c1/borderlands\_4\_base85\_decoder.py](https://gitlab.nicnl.com/Nicnl/borderlands_4_item_tinker/-/blob/5b33bbbf73c90c387e239394d86279d2aa6ff2c1/borderlands_4_base85_decoder.py)

The encoding is not yet available in python format.  
However the online webtool is available at this link: [https://borderlands4-serial-comparator.nicnl.com/](https://borderlands4-serial-comparator.nicnl.com/)  
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
Basically, selling a **looted** item to a vending machine and buying it back **changes the serial**.  
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

Those two serials looks completely different, despite being the **exact same** item.  
As you will see below, only one combinations is able to align and match those two completely : big-endian + bit-mirror.

Note: the actual hex content is not the important part. What matters is how good those items match.  
Despite the serials being different they were KNOWN identical items, meaning the underlying data HAD to be very similar.  
This is what we aimed for: we adjusted our decoding until both the original and the buyback items matched.


#### <span style="color: rgb(35, 111, 161);">Little-endian</span> + <span style="color: rgb(224, 62, 45);">no bit-mirror</span>:

[![image.png](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/scaled-1680-/6mlimage.png)](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/6mlimage.png)

```
Original: 8060e084220e460           9ca0d9ccca1d42a89a1e6a26ea1eea1f2a0e6a0c221c6a17200
Buyback:  8060e084a20e4609ccc2204ca89ca0d926ea1d421f2a1e6a0c2a1eea172a0e6a      6a1 c02
Diff:     ========!======+++++++++++======!!!=====!!!=====!!!======!======++++++===+!=!
Overall - Match: 60% / Diff: 17% / Added: 23%
```



#### <span style="color: rgb(35, 111, 161);">Little-endian</span> + <span style="color: rgb(22, 145, 121);">bit-mirror</span>:

[![image.png](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/scaled-1680-/eXuimage.png)](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/eXuimage.png)


```
Original: 010607214470629053b03933852b5491856745768577854f056705438463854e0       0
Buyback:  0106072145706290   334304321539059b6457b842f854785630547857e8547056563840
Diff:     =========!======+++!=!=!!!=!=!=!!!!!===!=!!!===!!==!===!=!!!===!=+++++++=
Overall - Match: 52% / Diff: 34% / Added: 14%
```


#### <span style="color: rgb(22, 145, 121);">Big-endian </span>+ <span style="color: rgb(224, 62, 45);">no bit-mirror</span>:

[![image.png](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/scaled-1680-/tFXimage.png)](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/tFXimage.png)

```
Original: 84e0608009460e   22cc9c0dca892ad4a16ea2e6a1f2a1eea1c2a0e6a072a1c621 00
Buyback:  84e0608009460ea24c20c2ccd9a09ca8421dea266a1e2a1fea1e2a0c6a0e2a176a1c02
Diff:     ==============+++!=!=!=!=!=!=!=!=!=!===!===!===!===!===!===!===!=!=+=!
Overall - Match: 67% / Diff: 27% / Added: 6%
```

#### <span style="color: rgb(22, 145, 121);">Big-endian </span>+ <span style="color: rgb(22, 145, 121);">bit-mirror</span>:

[![image.png](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/scaled-1680-/ooLimage.png)](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/ooLimage.png)

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
[https://gitlab.nicnl.com/Nicnl/borderlands\_4\_item\_tinker/-/blob/15dc834e5daf3a32d275a9335fcaaa05d4902038/lib/b85.js](https://gitlab.nicnl.com/Nicnl/borderlands_4_item_tinker/-/blob/15dc834e5daf3a32d275a9335fcaaa05d4902038/lib/b85.js)  
  
Unit tests available here:  
[https://gitlab.nicnl.com/Nicnl/borderlands\_4\_item\_tinker/-/blob/15dc834e5daf3a32d275a9335fcaaa05d4902038/unit\_test.js](https://gitlab.nicnl.com/Nicnl/borderlands_4_item_tinker/-/blob/15dc834e5daf3a32d275a9335fcaaa05d4902038/unit_test.js)

### 6. Credits

@Sparkie for his initial base85 implementation + his alphabet  
@InflamedSebi for his the bit-mirror breakthrough  
@Nicnl for additional work and webtool

# Data Types

#### 1. Introduction

The serials are made of values (integers, etc) serialized in blocks :

- Each value has its own block.
- The block size depends on: 
    - The major type : three bits.
    - Its optional parameters : arbitrary number of bits.

```
Major type
v
100 .......
    ^
    Variable amount of bits
```

##### 1.1 Varint5

The varint5 encodes 16-bit integers into blocks of 5-bits:

- <span style="color: rgb(22, 145, 121);">Confirmed (can be swapped with Varbit5, notably in the item level)</span>
- Major type is: `100`
- It is followed by at least one block of 5-bits: 
    - LSB is the continuation bit: 
        - 1 =&gt; there is another block ahead.  
            (Up to 3 additional blocks, 4 blocks total.)
        - 0 =&gt; end of payload.
    - The 4 remaining bits is part of the payload in LSB-first.

```
Type     Stop
vvv      v
100  11000
     ^^^^
     data
=bin:1100
=int:3
```

```
  Continue      Stop
         v      v
100  10001  00010
     ^^^^   ^^^^
     data   data
=bin:1000   0001
=int:129
```

```
                              Stop
         v      v      v      v
100  01001  00001  00001  00000
     ^^^^   ^^^^   ^^^^   ^^^^
     data   data   data   data
=bin:0100   0000   0000   0000
=int:2
```

##### 1.1 Varbit5

- <span style="color: rgb(22, 145, 121);">Confirmed (can be swapped with Varint5, notably in the item level)</span>
- Major type is: `110`
- Is followed by <span style="text-decoration: underline;">exactly one</span> block of 5-bits. 
    - =&gt; length of the payload ahead. (LSB-first)
- Is followed by a variable amount of bits =&gt; payload. 
    - Payload is ordered LSB-first.

```
Type   Length   Data
vvv    vvvvv    vvv
110    11000    101
                ^^^
           =bin:101
           =int:5
```

#### 2. Complex Objects

Some data might be composed from multiple independent values. Those would need a starting flag and a terminating flag to work.

##### 2.1 Array


- There should be arrays, however it is unclear if the are typed or untyped / ordered or unordered.
- Major type is: `unknown`
- Terminator: `000` (probably)

##### 2.2 Struct


- Structures consist of a predefined subset of other types.
- Major type is: `001` (probably)
- Is followed by <span style="text-decoration: underline;">exactly one</span> block of 4-bits. 
    - =&gt; ID of the structure to read. (LSB)
- Terminator: `000` (probably)

#### 3. Unverified major types

- `010` =&gt; Sebi: static 2-bit?
- `011` =&gt; Nicnl: unknown use
- `101` =&gt; Nicnl: start of list ? start of array ? start of parts ?
- `000` =&gt; Nicnl: End of stream? End of structure? End of array? Padding? Section delimiter?
- 

**<span style="color: rgb(22, 145, 121);">Good:</span>** Some major types can be swapped, notably varint5 and varbit5 in the item level.  
**<span style="color: rgb(186, 55, 42);">Bad:</span>** However we were unable to swap a varint5 (nor a varbit5) with the suspected `001` static 4-bit value.  
Some major types are more efficient depending on the integer =&gt; the game sometimes re serializes to shorter versions.  
One example is the item type which switches from Varint5 to Varbit5 once it exceeds a value of 255.

##### 3.2 Missing types

- Array
- Boolean
- Bitmap

##### 3.1 Major type 011

Has been seen with various lengths:

```
Size 25:
011 0000001100011110000001011
011 0001011111111100000001011
011 0011011101010101000001011
011 0001011110110001000001011

Size 24 (last bits aligns well)
011 1010010101001111 00001011

Size 19
011 0000000011001000001
```

#### 4. Credits:

@Nicnl for figuring out the var<span style="text-decoration: underline;">int</span> logic.  
@InflamedSebi for figuring out the var<span style="text-decoration: underline;">bit</span> logic.

# Item Types and Manufacturers

#### 1. Introduction

**<span style="color: rgb(230, 126, 35);">Observed:</span>** serials always starts with this static prefix: `001 0000`  
**<span style="color: rgb(22, 145, 121);">Verified:</span>** the item type is after this prefix, serialized as an integer in [Varint5](https://bookstack.nicnl.com/books/borderlands-4-item-serials/page/data-types#bkmrk-2.1-varint5) or [Varbit5](https://bookstack.nicnl.com/books/borderlands-4-item-serials/page/data-types#bkmrk-2.1-varbit5) format.  
After deserialization, the integer item type has to be searched in a lookup table.

```
Daedalus SMG:
001 0000 100 00101 10000 ...
         ^^^^^^^^^^^^^^^
         varint5 = 20
```

```
Ripper Repkit:
001 0000 110 10010 010010001
         ^^^^^^^^^^^^^^^^^^^
         varbit5 = 274
```

#### 2. Lookup table

TODO: build the lookup table out of known headers.

```
node extract_unique_bitpatterns_until_marker.js
Unique patterns found: 69
00100001001100001100 => Jakobs Pistol
00100001000010001100 => Order Pistol
00100001000100001100 => Daedalus Pistol
00100001000110001100 => Torgue Pistol
00100001001010001100 => Tediore Pistol
00100001101001001010000101100 => Maliwan Repkit
00100001101001010010000101100 => Jakobs Repkit
00100001101001010110000101100 => Vladof Repkit
00100001101001010111000101100 => Order Repair Kit,Vladof Repkit
00100001101001010100000101100 => Torgue Repkit
00100001101001010101000101100 => Daedalus Repkit
00100001101001001001000101100 => Ripper Repkit
00100001101001001000100101100 => Tediore Repkit
0010000100101011000001100 => Maliwan SMG
0010000100001011000001100 => Daedalus SMG
0010000100011011000001100 => Vladof SMG
0010000100110011000001100 => Ripper SMG
00100001101001000000000101100 => Exo Class Mod
00100001001011001100 => Daedalus Assault Rifle
0010000100110111000001100 => Jakobs Assault Rifle
00100001001111001100 => Order Assault Rifle
0010000100100011000001100 => Torgue Assault Rifle
00100001000111001100 => Tediore Assault Rifle
0010000100010011000001100 => Vladof Assault Rifle
00100001000101001100 => Maliwan Shotgun
00100001000011001100 => Torgue Shotgun
00100001000001001100 => Daedalus Shotgun
00100001001001001100 => Jakobs Shotgun
00100001001101001100 => Tediore Shotgun
00100001001110001100 => Ripper Shotgun
00100001101001011010000101100 => Jakobs Grenade
00100001101001011000100101100 => Vladof Grenade
00100001101001011101100101100 => Tediore Grenade
00100001101001001101000101100 => Ripper Grenade
00100001101001000001000101100 => Order Grenade
00100001101001001010100101100 => Torgue Grenade
00100001101001011100000101100 => Maliwan Grenade
00100001101001001110000101100 => Daedalus Grenade
00100001101001010100100101100 => Order Shield
00100001101001010000010101100 => Torgue Shield
00100001101001011111000101100 => Tediore Shield
00100001101001001001100101100 => Jakobs Shield
00100001101001011011000101100 => Vladof Shield
00100001101001011101000101100 => Maliwan Shield
00100001101001000110100101100 => Ripper Shield
00100001101001000011100101100 => Daedalus Shield
0010000100111011000001100 => Ripper Sniper
0010000100100111000001100 => Maliwan Sniper
0010000100000011000001100 => Vladof Sniper
0010000100010111000001100 => Order Sniper
0010000100000111000001100 => Jakobs Sniper
00100001101001001101100101100 => Vladof Enhancement
00100001101001011110100101100 => Torgue Enhancement
00100001101001000100100101100 => Tediore Enhancement
00100001101001000010100101100 => Ripper Enhancement
00100001101001010011000101100 => Order Enhancement
00100001101001011110000101100 => Maliwan Enhancement
00100001101001000110000101100 => Jakobs Enhancement
00100001101001000010000101100 => Hyperion Enhancement
00100001101001011010100101100 => Daedalus Enhancement
00100001101001001111000101100 => CoV Enhancement
00100001101001000111000101100 => Atlas Enhancement
0010000100111111111001100 => Forgeknight Class Mod
00100001101001011000000101100 => Gravitar Class Mod
0010000100011111111001100 => Siren Class Mod
00100001101001001011000101100 => Vladof Heavy Weapon
00100001101001010001000101100 => Torgue Heavy Weapon
00100001101001010000100101100 => Maliwan Heavy Weapon
00100001101001011001000101100 => Ripper Heavy Weapon
```

# Item Level

Description of how the levels are encoded in the binary stream.

### 1. Layout:

##### 1.1. Find the position of the level-bits:  


The bits governing the level are positioned seemingly randomly, see below:

```
=============================================LLLLc==============
=================================================LLLLcLLLLc=====
========================================LLLLcLLLLc==============
```

We have not figured out how the header decodes, so positioning the level bits is tricky.  
However, there is a workaround: the levels bits seems always positioned after a specific bit pattern: `00000011001000001100`  
The level bits are always positioned after this marker in a varint datatype.

```
                                marker
                         vvvvvvvvvvvvvvvvvvvv
=========================00000011001000001100LLLLcLLLLc=========
                                             ^^^^^
                                           level bits
```

Important: the item level is encoded using the "varint" datatype, read here:  
[https://bookstack.nicnl.com/books/borderlands-4-item-serials/page/data-types](https://bookstack.nicnl.com/books/borderlands-4-item-serials/page/data-type-varint5)

### 2. Examples:

Below are a few examples of how to decode the level of actual existing items.

```
Step 1:
Raw serial: @Ugr$xKm/)}}$pj({_X>Jcq0UExO{SqiosR~Z6aW


Step 2: extract the first bits using the webtool:
00100001101001010111000101100000000110010000011000100111000001001001001100100000010


Step 3: workaround for finding the level bits, search for this string: 00000011001000001100
Found here:
00100001101001010111000101100000000110010000011000100111000001001001001100100000010
                             ^^^^^^^^^^^^^^^^^^^^


Step 4: the level bits are right after the marker
00100001101001010111000101100000000110010000011000100111000001001001001100100000010
                             --------------------LLLLc
       continuation bit=1, we must read 5 more bits -|


Step 5: continuation bit was 1, we must continue
00100001101001010111000101100000000110010000011000100111000001001001001100100000010
                             -------------------------LLLLc
                     continuation bit=0, we done reading -|


Step 4: assemble the data
LLLLc LLLc: 01001 11000

Step 5: discard the continuation bit, we don't need them anymore
LLLL  LLLL: 0100  1100

Step 6: reverse the string:
01001100 => 00110010

Step 7: binary to decimal
00110010 => 50

=> Item is level 50
```

```
serial: @Ugd77*Fg_4rx=zp;RG}I*T&N7HBq}9pC29=n4yqJt7iug5

search marker:      00000011001000001100

                        found here
                    vvvvvvvvvvvvvvvvvvvv
0010000100111000110000000011001000001100 01111 100000010001000011001011101....
                                         LLLLc LLLLc
                           level bits:   01111 10000
             discard continuation bit:   0111  1000

extracted:   01111000
reverse:     00011110
to decimal:  30
=> Item is level 30
```

Using this method, we have been able to take an existing serial, and forge all items from level 1 to level 50:

```
Item: Killshot Vivisecting Throwing Knife
Level 1:   @Ugr$WBm/!9x!X=5&qXxA;nj3OOD#<4R
Level 2:   @Ugr$WBm/!Fz!X=5&qXxA;nj3OOD#<4R
Level 3:   @Ugr$WBm/!L#!X=5&qXxA;nj3OOD#<4R
Level 4:   @Ugr$WBm/!R%!X=5&qXxA;nj3OOD#<4R
Level 5:   @Ugr$WBm/!X(!X=5&qXxA;nj3OOD#<4R
Level 6:   @Ugr$WBm/!d*!X=5&qXxA;nj3OOD#<4R
Level 7:   @Ugr$WBm/!j-!X=5&qXxA;nj3OOD#<4R
Level 8:   @Ugr$WBm/!p<!X=5&qXxA;nj3OOD#<4R
Level 9:   @Ugr$WBm/!v>!X=5&qXxA;nj3OOD#<4R
Level 10:  @Ugr$WBm/!#@!X=5&qXxA;nj3OOD#<4R
Level 11:  @Ugr$WBm/!*_!X=5&qXxA;nj3OOD#<4R
Level 12:  @Ugr$WBm/!>{!X=5&qXxA;nj3OOD#<4R
Level 13:  @Ugr$WBm/!{}!X=5&qXxA;nj3OOD#<4R
Level 14:  @Ugr$WBm/#30!X=5&qXxA;nj3OOD#<4R
Level 15:  @Ugr$WBm/#92!X=5&qXxA;nj3OOD#<4R
Level 16:  @Ugr$WBm/$Qa!X=5&qXxA;nj3OOD#<4R
Level 17:  @Ugr$WBm/$Wc!X=5&qXxA;nj3OOD#<4R
Level 18:  @Ugr$WBm/$ce!X=5&qXxA;nj3OOD#<4R
Level 19:  @Ugr$WBm/$ig!X=5&qXxA;nj3OOD#<4R
Level 20:  @Ugr$WBm/$oi!X=5&qXxA;nj3OOD#<4R
Level 21:  @Ugr$WBm/$uk!X=5&qXxA;nj3OOD#<4R
Level 22:  @Ugr$WBm/$!m!X=5&qXxA;nj3OOD#<4R
Level 23:  @Ugr$WBm/$)o!X=5&qXxA;nj3OOD#<4R
Level 24:  @Ugr$WBm/$=q!X=5&qXxA;nj3OOD#<4R
Level 25:  @Ugr$WBm/$`s!X=5&qXxA;nj3OOD#<4R
Level 26:  @Ugr$WBm/%1u!X=5&qXxA;nj3OOD#<4R
Level 27:  @Ugr$WBm/%7w!X=5&qXxA;nj3OOD#<4R
Level 28:  @Ugr$WBm/%Dy!X=5&qXxA;nj3OOD#<4R
Level 29:  @Ugr$WBm/%J!!X=5&qXxA;nj3OOD#<4R
Level 30:  @Ugr$WBm/%P$!X=5&qXxA;nj3OOD#<4R
Level 31:  @Ugr$WBm/%V&!X=5&qXxA;nj3OOD#<4R
Level 32:  @Ugr$WBm/&nF!X=5&qXxA;nj3OOD#<4R
Level 33:  @Ugr$WBm/&tH!X=5&qXxA;nj3OOD#<4R
Level 34:  @Ugr$WBm/&zJ!X=5&qXxA;nj3OOD#<4R
Level 35:  @Ugr$WBm/&(L!X=5&qXxA;nj3OOD#<4R
Level 36:  @Ugr$WBm/&<N!X=5&qXxA;nj3OOD#<4R
Level 37:  @Ugr$WBm/&_P!X=5&qXxA;nj3OOD#<4R
Level 38:  @Ugr$WBm/(0R!X=5&qXxA;nj3OOD#<4R
Level 39:  @Ugr$WBm/(6T!X=5&qXxA;nj3OOD#<4R
Level 40:  @Ugr$WBm/(CV!X=5&qXxA;nj3OOD#<4R
Level 41:  @Ugr$WBm/(IX!X=5&qXxA;nj3OOD#<4R
Level 42:  @Ugr$WBm/(OZ!X=5&qXxA;nj3OOD#<4R
Level 43:  @Ugr$WBm/(Ub!X=5&qXxA;nj3OOD#<4R
Level 44:  @Ugr$WBm/(ad!X=5&qXxA;nj3OOD#<4R
Level 45:  @Ugr$WBm/(gf!X=5&qXxA;nj3OOD#<4R
Level 46:  @Ugr$WBm/(mh!X=5&qXxA;nj3OOD#<4R
Level 47:  @Ugr$WBm/(sj!X=5&qXxA;nj3OOD#<4R
Level 48:  @Ugr$WBm/)-_!X=5&qXxA;nj3OOD#<4R
Level 49:  @Ugr$WBm/)@{!X=5&qXxA;nj3OOD#<4R
Level 50:  @Ugr$WBm/)}}!X=5&qXxA;nj3OOD#<4R

Note: those items between level 1 and 15 have the redundant zero-value varint mentioned.
Those items are going to get reserialized/collapsed to a shorter serial when loading in-game.
```

We were also able to generate "unholy" serials:

```
Level 64:  @Ugr$WBm/!4<fC!f)LXR5M`e<&*6{#ej00
Note: did not spawn, game probably have a hardcoded limit.

Level 0:   @Ugr$WBm/!4;fC!f)LXR5M`e<&*6{#ej00
Note: did spawn in-game, no level shown on screen, and had less damage than its level 1 counterpart.

Level -3:  @Ugr$WBm/*(<j/i6}LXR5M`e<&*6{#ej00
Note: did spawn in game, shown as level negative 3, and had even less damage than the level 0 and 1 combined.

Minimum value of int16: @Ugr$WBm/!4;hzOS?LXR5M`e<&*6{#ej00
Note: DID SPAWN AS LEVEL -32768. THIS IS FUCKING UNHOLY.
(See screenshot below)
```

[![image.png](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/scaled-1680-/LV1image.png)](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/LV1image.png)

###   
3. Discovery:

How did we discover this?

We performed bitswapping on existing weapons to create variant with different levels.  
We noticed that the bits governing the levels were not aligned:

```
=============================================!!!!1!!000=========
=================================================!!!!1!!000=====
========================================!!!!1!!000==============
```

Starting from there, we made two observations:

1. There was a floating "1" in the middle of the level bits, suggesting varint fuckery.
2. A bitswapped level 3 item got reserialized to a shorter serial.  
    More precisely, a blocks of five "0" were removed + the "floating" bit got set to zero.

Those to elements were our Rosetta stone for understanding how this 5-bit varint worked.

```
                                               altered level bits
                                                   vvvv   vv
0010000110100101101000010110000000011001000001100  1100 1 00000  00100010 ... 10000 000
0010000110100101101000010110000000011001000001100  1100 0        00100010 ... 10000
=================================================  ==== ! -----  ======== ... ===== ---   
                                                       /       \                       \ padding removed so is multiple of 8 bits
                                                      /         \
                         "floating bit" set to zero -/           \- block of 5 bits removed 
```

# Item Parts

Not really known yet.

By bitswapping items, we observed a lot of weird stuff:

- Items with wrong parts at the wrong place (a magazine instead of a shoulder rest).
- Items with missing parts
- Item with multiple different stacked parts at the same place (3D models overlapping and all)

Current (**<span style="color: rgb(224, 62, 45);">unverified</span>**) theory :

1. The serials features a modular parts system.
2. Parts are described by a combination of two data: 
    1. A position : scope, grip, barrel, etc
    2. A unique identifier: round scope, COV magazine, long scope, etc...

Items worth analyzing:

We bitswapped and corrupted some items, until they got reserialized and collapsed with less parts.

```
Original item: Killshot Vivisecting Throwing Knife
  4 perks:  @Ugr$WBm/$!m!X=5&qXxA;nj3OOD#<4R

Altered and collapsed through reserialization:
  3 perks:  @Ugr$WBm/$!m!X=5&qXxA;nj3OODgg
  2 perks:  @Ugr$WBm/$!m!X=5&qXxA;nj3Nj00
  1 perk:   @Ugr$WBm/$!m!X=5&qXq#
```

[![image.png](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/scaled-1680-/RiEimage.png)](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/RiEimage.png)[![image.png](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/scaled-1680-/FF1image.png)](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/FF1image.png)[![image.png](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/scaled-1680-/fSnimage.png)](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/fSnimage.png)

The differences are located at the end of the serial.  
We don't know the meaning of it yet.

The "2 perk" to "1 perk" diff is strange, a lot of bits got removed.  
Does it mean the entire "parts" subsection got removed?

[![image.png](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/scaled-1680-/KgRimage.png)](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/KgRimage.png)

[![image.png](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/scaled-1680-/hZvimage.png)](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/hZvimage.png)

[![image.png](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/scaled-1680-/8ITimage.png)](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/8ITimage.png)

# Item Skills

For Grenades without firmware, they seem to be at the end of the serial.  
  
There were recent tests with a Jacobs knife: @Ugr$WBm/$!m!X=5&amp;qXxA;nj3OOD#&lt;4R  
The following set of bitswapped versions all have different skills and seem to be legit:

```
        slot_0:
          serial: '@Ugr$WBm/$!m!X=5&qYkw`nj3OOD#<4R'
        slot_1:
          serial: '@Ugr$WBm/$!m!X=5&qb9XJnj3OOD#<4R'
        slot_2:
          serial: '@Ugr$WBm/$!m!X=5&qXxA;nj3OOD#<4R'
        slot_3:
          serial: '@Ugr$WBm/$!m!X=5&qXxA;8XIy&D#<4R'
        slot_4:
          serial: '@Ugr$WBm/$!m!X=5&qXxA;njdmSD#<4R'
        slot_5:
          serial: '@Ugr$WBm/$!m!X=5&qXxA;ni_IND#<4R'
        slot_6:
          serial: '@Ugr$WBm/$!m!X=5&qXxA;nmckuD#<4R'
        slot_7:
          serial: '@Ugr$WBm/$!m!X=5&qXxA;nj7*(D#<4R'
        slot_8:
          serial: '@Ugr$WBm/$!m!X=5&qXxA;nj11jD#<4R'
        slot_9:
          serial: '@Ugr$WBm/$!m!X=5&qXxA;nj2C@D#<4R'
        slot_10:
          serial: '@Ugr$WBm/$!m!X=5&qXxA;nj2z8D#<4R'
        slot_11:
          serial: '@Ugr$WBm/$!m!X=5&qXxA;nj3OQD#<4R'
        slot_12:
          serial: '@Ugr$WBm/$!m!X=5&qXxA;nj3OOBFQHJ'
        slot_13:
          serial: '@Ugr$WBm/$!m!X=5&qXxA;nj3OOF3BeV'
        slot_14:
          serial: '@Ugr$WBm/$!m!X=5&qXxA;nj3OOD9I-P'
        slot_15:
          serial: '@Ugr$WBm/$!m!X=5&qXxA;nj3OOI>{#h'
        slot_16:
          serial: '@Ugr$WBm/$!m!X=5&qXxA;nj3OODoG~*'
        slot_17:
          serial: '@Ugr$WBm/$!m!X=5&qXxA;nj3OODv2im'
        slot_18:
          serial: '@Ugr$WBm/$!m!X=5&qXxA;nj3OOD#;}P'
        slot_19:
          serial: '@Ugr$WBm/$!m!X=5&qXxA;nj3OOD#<1Q'
```

After inspecting the changes and matching the same skill on different slots/items

```
Grenades (Type B)
| End bit of level                    | rarity 2 bit (only green and purple)
|<--------36-bit-?------------------><><-----?-----------?-----------?----><---skill--><---skill--><---skill--><---skill--><---?----->
X000000000000000000000000000000000000XX00000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000

Grenade parts 12 bit stacked directly ontop of each other
<---skill-->
100111011100 spawn searching Micro rockets
001001110100 Express coldown
100111010100 damage boost
010011101001 pierce 5s crit
001001111100 grenade crit damage up
001110110000 jacobs - crit on weak points
000110110000 spawn more grenades each impact
100011010100 spawn radiance orbs
100110010100 spawn corrosion rays
100101010100 spawn cryo puddles
100111110100 repeater downward grenades mid flight
010010111001 increased knockback
010010001001 fractur spawn 3 elemental pillar
010000101001 supress target damage
001110110000 search second spawned grenade homes
001010110000 Duration lingering grenades up
001111110000 jumps and explodes multiple times
001001101100 crit chance
001000111100 grenade lifesteal up


<-----?-----------?-----------?---->
100010101100100101011010111110001011 Juggling Legendary
100010101100000101011010111110001011 base
```

# Item Firmware

not much known yet

but this looks to be a good start:  
@Uge8^+m/)}}!c178NkyuCbwKf&gt;IWYh  
@Uge8^+m/)}}!axR1DpKvM1BxF\_41oav

[![image.png](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/scaled-1680-/GUnimage.png)](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/GUnimage.png)

[![image.png](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/scaled-1680-/Bgrimage.png)](https://bookstack.nicnl.com/uploads/images/gallery/2025-10/Bgrimage.png)

# Item Rarity

not much known yet, but:  
  
green blue and purple seem to have a 2 bit rarity marker, which affects base stats of the weapon

```
Grenades                                       | rarity 2 bit
<-level--><-------36-bit-?-------------------><><-----?-----------?...
0000X0000X000000000000000000000000000000000000XX0000000000000000000...
```

however locating the rarity bit on common or legendary is quite tricky , they might not have them.

here is a set of smgs:

1 white  
2 green  
2 purple

```
        slot_0:
          serial: '@Ugw$Yw3C0Q{4D197jVe^44mDipQ7KWI+Jnl4Du){0000'
        slot_1:
          serial: '@Ugw$Yw3C0Q{jKmBojVe^48Z}htQ8Q5/QJ*@4nuDr^Du){K000'
        slot_2:
          serial: '@UgwSAs3C0Q{%<T>Oi/U7Z)TZX3a-q(l>LCC'
        slot_3:
          serial: '@Ugw$Yw3C0Q{OqUJ{jVe^48Z}(#Q7KWIs)Ndf`h@@'
        slot_4:
          serial: '@Ugw$Yw3C0Q{jI0JKjVe^47S*VsLXS#`8j1SU8Ppt9F4Q^%'

```

# Stuff to investigate

# Modified header

```
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
have I created a level-less item?????

```

# Item Parts

#### 1. Grenade parts

<table border="1" id="bkmrk-varint5-%2F-varbit5-in" style="border-collapse: collapse; width: 100%;"><colgroup><col style="width: 16.2004%;"></col><col style="width: 6.55165%;"></col><col style="width: 15.2475%;"></col><col style="width: 41.9306%;"></col><col style="width: 8.57722%;"></col><col style="width: 11.5542%;"></col></colgroup><tbody><tr><td>Varint5 / Varbit5</td><td>Int</td><td>Prefix</td><td>Description</td><td>UI Stack</td><td>Behaviour</td></tr><tr><td>`100 10101 00100`</td><td><span style="color: rgb(230, 126, 35);">**Todo**</span></td><td>+Penetrator</td><td>Damage to the impacted target are automatic critical hits for 5s</td><td>**<span style="color: rgb(186, 55, 42);">No</span>**</td><td>**<span style="color: rgb(230, 126, 35);">Unverified</span>**</td></tr><tr><td>`100 11111 00100`  
</td><td>**<span style="color: rgb(230, 126, 35);"><span style="color: rgb(186, 55, 42);"><span style="color: rgb(35, 111, 161);"><span style="color: rgb(230, 126, 35);">Todo</span></span></span></span>**</td><td>+Killshot</td><td>Grenade Critical Damage increased by 80%</td><td><span style="color: rgb(22, 145, 121);">**Yes**</span></td><td>**<span style="color: rgb(22, 145, 121);">Stack</span>**</td></tr><tr><td>`100 11101 01000`  
</td><td><span style="color: rgb(186, 55, 42);">**<span style="color: rgb(35, 111, 161);"><span style="color: rgb(230, 126, 35);">Todo</span></span>**</span></td><td>+Wounding</td><td>Damage taken by the impacted target is increased by +15% for 15s</td><td>**<span style="color: rgb(186, 55, 42);">No</span>**</td><td>**<span style="color: rgb(230, 126, 35);">Unverified</span>**</td></tr><tr><td>`100 11101 10000`  
</td><td><span style="color: rgb(230, 126, 35);">**Todo**</span></td><td><span style="color: rgb(186, 55, 42);">**None**</span></td><td>Item unchanged. (visually + description)</td><td>**<span style="color: rgb(186, 55, 42);">No</span>**</td><td>**<span style="color: rgb(230, 126, 35);">Unverified</span>**</td></tr></tbody></table>
