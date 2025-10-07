const HANDLE_PREFIX = true;
let REVERSE_BITS = true;

// Byte order configuration: [0, 1, 2, 3] represents the position mapping
// Default [0, 1, 2, 3] = big-endian (most significant byte first)
// [3, 2, 1, 0] = little-endian (least significant byte first)
// You can use any permutation like [2, 3, 0, 1] for custom byte swapping
let BYTE_ORDER = [0, 1, 2, 3];

function base85ChangeByteOrder(newOrder) {
    if (newOrder.length !== 4 || new Set(newOrder).size !== 4 || !newOrder.every(i => i >= 0 && i < 4)) {
        throw new Error("Invalid byte order configuration");
    }
    BYTE_ORDER = newOrder;
}

function base85GetByteOrder() {
    return BYTE_ORDER;
}

//base85GetReverseBits, base85SetReverseBits
function base85GetReverseBits() {
    return REVERSE_BITS;
}

function base85SetReverseBits(value) {
    REVERSE_BITS = value;
}

// Helper function to apply byte order configuration
function applyByteOrder(bytes) {
    return [
        bytes[BYTE_ORDER[0]],
        bytes[BYTE_ORDER[1]],
        bytes[BYTE_ORDER[2]],
        bytes[BYTE_ORDER[3]]
    ];
}

// Helper function to reverse byte order configuration (for decoding)
function reverseByteOrder(bytes) {
    const result = new Array(4);
    result[BYTE_ORDER[0]] = bytes[0];
    result[BYTE_ORDER[1]] = bytes[1];
    result[BYTE_ORDER[2]] = bytes[2];
    result[BYTE_ORDER[3]] = bytes[3];
    return result;
}

/*
int b85_decode(char *string,uint size,byte *data)
{
  char cVar1;
  longlong lVar2;
  uint uVar3;
  uint char_idx;
  uint working_u32;
  int iVar4;
  uint uVar5;
  ulonglong uVar6;
  ulonglong idx;

  iVar4 = (int)data;
  if (b85_reverse_lookup_initalized == '\0') {
    lVar2 = 0;
    do {
      cVar1 = (char)lVar2;
      (&b85_reverse_lookup)
      [(byte)"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~"
             [lVar2]] = cVar1;
      (&b85_reverse_lookup)
      [(byte)"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~"
             [lVar2 + 1]] = cVar1 + '\x01';
      (&b85_reverse_lookup)
      [(byte)"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~"
             [lVar2 + 2]] = cVar1 + '\x02';
      (&b85_reverse_lookup)
      [(byte)"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~"
             [lVar2 + 3]] = cVar1 + '\x03';
      (&b85_reverse_lookup)
      [(byte)"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~"
             [lVar2 + 4]] = cVar1 + '\x04';
      lVar2 = lVar2 + 5;
    } while (lVar2 != 0x55);
    DAT_15117f6ec = DAT_15117f69f;
    b85_reverse_lookup_initalized = '\x01';
  }
  if (size == 0) {
b85_decode_quit:
    return (int)data - iVar4;
  }
  uVar6 = 0;
LAB_1429773c9:
  working_u32 = 0;
  char_idx = 0;
  idx = uVar6;
  do {
    uVar6 = idx + 1;
    if ((-1 < (longlong)string[idx]) && ((byte)(&b85_reverse_lookup)[string[idx]] < 0x56)) {
      working_u32 = working_u32 * 0x55 + (uint)(byte)(&b85_reverse_lookup)[string[idx]];
      char_idx = char_idx + 1;
      if (char_idx == 5) break;
    }
    idx = uVar6;
    if (uVar6 == size) {
      if ((int)char_idx < 1) goto b85_decode_quit;
      if (char_idx != 5) {
        uVar3 = 5 - char_idx;
        if ((uVar3 & 7) != 0) {
          uVar5 = 0;
          do {
            working_u32 = working_u32 * 0x55 + 0x7e;
            uVar5 = uVar5 + 1;
          } while ((uVar3 & 7) != uVar5);
          uVar3 = uVar3 - uVar5;
        }
        if (4 < char_idx) {
          do {
            working_u32 = working_u32 * 0x717f0261 + 0x2a3e8390;
            uVar3 = uVar3 - 8;
          } while (uVar3 != 0);
        }
        if (((char_idx != 1) && (*data = (char)(working_u32 >> 0x18), 2 < (int)char_idx)) &&
           (*(char *)((longlong)data + 1) = (char)(working_u32 >> 0x10), char_idx != 3)) {
LAB_142977442:
          *(char *)((longlong)data + 2) = (char)(working_u32 >> 8);
        }
        data = (byte *)((longlong)data + (ulonglong)(char_idx - 1));
        goto b85_decode_quit;
      }
      *data = (char)(working_u32 >> 0x18);
      *(char *)((longlong)data + 1) = (char)(working_u32 >> 0x10);
      goto LAB_142977442;
    }
  } while( true );
  *(uint *)data =
       working_u32 >> 0x18 | (working_u32 & 0xff0000) >> 8 | (working_u32 & 0xff00) << 8 |
       working_u32 * 0x1000000;
  data = (byte *)((longlong)data + 4);
  if (uVar6 == size) goto b85_decode_quit;
  goto LAB_1429773c9;
}

int b85_encode(byte *data,uint len,char *str)

{
  ushort uVar1;
  uint last_u32;
  int iVar2;
  uint extra_bytes;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint working_u32;

  iVar2 = (int)str;
  extra_bytes = len & 3;
  if (3 < len) {
    working_u32 = len >> 2;
    do {
      uVar3 = *(uint *)data;
      uVar3 = uVar3 >> 0x18 | (uVar3 & 0xff0000) >> 8 | (uVar3 & 0xff00) << 8 | uVar3 << 0x18;
      data = (byte *)((longlong)data + 4);
      uVar4 = uVar3 % 0x31c84b1;
      uVar5 = uVar4 % 0x95eed;
      uVar6 = uVar5 % 0x1c39;
      *str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~"
             [uVar3 / 0x31c84b1];
      str[1] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/} ~"
               [(ulonglong)uVar4 / 0x95eed];
      str[2] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/} ~"
               [(ulonglong)uVar5 / 0x1c39];
      str[3] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/} ~"
               [uVar6 / 0x55];
      str[4] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/} ~"
               [uVar6 % 0x55];
      str = str + 5;
      working_u32 = working_u32 - 1;
    } while (working_u32 != 0);
  }
  if (extra_bytes != 0) {
    last_u32 = (uint)(byte)*(uint *)data;
    if (extra_bytes != 1) {
      uVar1 = CONCAT11((byte)*(uint *)data,*(byte *)((longlong)data + 1));
      last_u32 = (uint)uVar1;
      if (extra_bytes != 2) {
        last_u32 = (uint)CONCAT21(uVar1,*(byte *)((longlong)data + 2));
      }
    }
    if (extra_bytes == 3) {
      working_u32 = last_u32 << 8;
    }
    else if (extra_bytes == 2) {
      working_u32 = last_u32 << 0x10;
    }
    else {
      working_u32 = 0;
      if (extra_bytes == 1) {
        working_u32 = last_u32 << 0x18;
      }
    }
    *str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~"
           [working_u32 / 0x31c84b1];
    str[1] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~"
             [(ulonglong)(working_u32 % 0x31c84b1) / 0x95eed];
    if (extra_bytes == 1) {
      str = str + 2;
    }
    else {
      working_u32 = (working_u32 % 0x31c84b1) % 0x95eed;
      str[2] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/} ~"
               [(ulonglong)working_u32 / 0x1c39];
      if (extra_bytes == 3) {
        str[3] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{ /}~"
                 [(working_u32 % 0x1c39) / 0x55];
        str = str + 4;
      }
      else {
        str = str + 3;
      }
    }
  }
  return (int)str - iVar2;
}


*/

const B85_CHARSET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~";

const reverseLookup = new Array(256).fill(0xFF);
for (let i = 0; i < B85_CHARSET.length; i++) {
    reverseLookup[B85_CHARSET.charCodeAt(i)] = i;
}

function b85Decode(string) {
    if (HANDLE_PREFIX) {
        if (string[0] !== '@' || string[1] !== 'U') return null;
        string = string.slice(2);
    }

    // Initialize reverse lookup table
    const result = [];
    let idx = 0;
    const size = string.length;

    while (idx < size) {
        let workingU32 = 0;
        let charCount = 0;

        // Collect up to 5 valid Base85 characters
        while (idx < size && charCount < 5) {
            const charCode = string.charCodeAt(idx);
            idx++;

            if (charCode >= 0 && reverseLookup[charCode] < 0x56) {
                workingU32 = workingU32 * 85 + reverseLookup[charCode];
                charCount++;
            }
        }

        if (charCount === 0) break;

        // Handle padding for incomplete groups
        if (charCount < 5) {
            const padding = 5 - charCount;
            for (let i = 0; i < padding; i++) {
                workingU32 = workingU32 * 85 + 0x7e; // '~' value
            }
        }

        if (charCount === 5) {
            // Full group - apply byte order transformation
            const standardBytes = [
                (workingU32 >>> 24) & 0xFF,
                (workingU32 >>> 16) & 0xFF,
                (workingU32 >>> 8) & 0xFF,
                (workingU32 >>> 0) & 0xFF
            ];

            const orderedBytes = reverseByteOrder(standardBytes);
            result.push(orderedBytes[0], orderedBytes[1], orderedBytes[2], orderedBytes[3]);
        } else {
            // Partial group - NO byte order transformation, just extract bytes normally
            const byteCount = charCount - 1;
            if (byteCount >= 1) result.push((workingU32 >>> 24) & 0xFF);
            if (byteCount >= 2) result.push((workingU32 >>> 16) & 0xFF);
            if (byteCount >= 3) result.push((workingU32 >>> 8) & 0xFF);
        }
    }

    // Reverse the bits in each byte
    // 76543210 => 01234567
    if (REVERSE_BITS) {
        for (let i = 0; i < result.length; i++) {
            let b = result[i];
            b = ((b & 0xF0) >> 4) | ((b & 0x0F) << 4);
            b = ((b & 0xCC) >> 2) | ((b & 0x33) << 2);
            b = ((b & 0xAA) >> 1) | ((b & 0x55) << 1);
            result[i] = b;
        }
    }

    // Convert byte array to hex string
    return result.map(b => b.toString(16).padStart(2, '0')).join('');
}

function b85Encode(hexString) {
    // Convert hex string to byte array
    const bytes = [];
    for (let i = 0; i < hexString.length; i += 2) {
        bytes.push(parseInt(hexString.substr(i, 2), 16));
    }

    // Reverse the bits in each byte
    // 76543210 => 01234567
    if (REVERSE_BITS) {
        for (let i = 0; i < bytes.length; i++) {
            let b = bytes[i];
            b = ((b & 0xF0) >> 4) | ((b & 0x0F) << 4);
            b = ((b & 0xCC) >> 2) | ((b & 0x33) << 2);
            b = ((b & 0xAA) >> 1) | ((b & 0x55) << 1);
            bytes[i] = b;
        }
    }

    const result = [];
    let idx = 0;
    const len = bytes.length;
    const extraBytes = len & 3;
    const fullGroups = len >> 2;

    // Process full 4-byte groups
    for (let i = 0; i < fullGroups; i++) {
        // Read 4 bytes from hex string
        const inputBytes = [bytes[idx], bytes[idx + 1], bytes[idx + 2], bytes[idx + 3]];
        idx += 4;

        // Apply byte order transformation
        const orderedBytes = applyByteOrder(inputBytes);

        // Combine into 32-bit value
        let u32 = (orderedBytes[0] << 24) | (orderedBytes[1] << 16) |
                  (orderedBytes[2] << 8) | orderedBytes[3];
        u32 = u32 >>> 0; // Convert to unsigned 32-bit

        // Divide by powers of 85 to extract Base85 digits
        result.push(B85_CHARSET[Math.floor(u32 / 52200625)]); // 85^4
        const rem1 = u32 % 52200625;
        result.push(B85_CHARSET[Math.floor(rem1 / 614125)]); // 85^3
        const rem2 = rem1 % 614125;
        result.push(B85_CHARSET[Math.floor(rem2 / 7225)]); // 85^2
        const rem3 = rem2 % 7225;
        result.push(B85_CHARSET[Math.floor(rem3 / 85)]); // 85^1
        result.push(B85_CHARSET[rem3 % 85]); // 85^0
    }

    // Handle remaining bytes (1-3) - NO byte order transformation for partial groups
    if (extraBytes !== 0) {
        let lastU32 = bytes[idx];
        if (extraBytes >= 2) {
            lastU32 = (lastU32 << 8) | bytes[idx + 1];
        }
        if (extraBytes === 3) {
            lastU32 = (lastU32 << 8) | bytes[idx + 2];
        }

        // Shift to appropriate position
        let workingU32;
        if (extraBytes === 3) {
            workingU32 = lastU32 << 8;
        } else if (extraBytes === 2) {
            workingU32 = lastU32 << 16;
        } else {
            workingU32 = lastU32 << 24;
        }
        workingU32 = workingU32 >>> 0;

        // Encode partial group
        result.push(B85_CHARSET[Math.floor(workingU32 / 52200625)]);
        const rem1 = workingU32 % 52200625;
        result.push(B85_CHARSET[Math.floor(rem1 / 614125)]);

        if (extraBytes >= 2) {
            const rem2 = rem1 % 614125;
            result.push(B85_CHARSET[Math.floor(rem2 / 7225)]);

            if (extraBytes === 3) {
                const rem3 = rem2 % 7225;
                result.push(B85_CHARSET[Math.floor(rem3 / 85)]);
            }
        }
    }

    if (HANDLE_PREFIX)
        return '@U' + result.join('');
    else
        return result.join('');
}

export { b85Decode, b85Encode, base85ChangeByteOrder, base85GetByteOrder, base85GetReverseBits, base85SetReverseBits };
