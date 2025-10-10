ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~"
BASE = 85
C4, C3, C2, C1 = 0x31c84b1, 0x95eed, 0x1c39, 0x55
lookup = {ch: i for i, ch in enumerate(ALPHABET)}


def b85_decode(string: str) -> bytes:
    data = bytearray()
    size = len(string)
    if size == 0:
        return bytes(data)
    idx = 0
    while True:
        working_u32 = 0
        char_idx = 0
        while True:
            if idx >= size:
                if char_idx < 1:
                    return bytes(data)
                if char_idx != 5:
                    uVar3 = 5 - char_idx
                    while uVar3 & 7:
                        working_u32 = (working_u32 * BASE + 0x7e) & 0xFFFFFFFF
                        uVar3 -= 1
                    while uVar3 > 0:
                        working_u32 = (working_u32 * 0x717f0261 + 0x2a3e8390) & 0xFFFFFFFF
                        uVar3 -= 8
                    if char_idx != 1:
                        data.append((working_u32 >> 24) & 0xFF)
                        if char_idx > 2:
                            data.append((working_u32 >> 16) & 0xFF)
                            if char_idx != 3:
                                data.append((working_u32 >> 8) & 0xFF)
                    else:
                        data.append((working_u32 >> 24) & 0xFF)
                    return bytes(data)
                data.append((working_u32 >> 24) & 0xFF)
                data.append((working_u32 >> 16) & 0xFF)
                data.append((working_u32 >> 8) & 0xFF)
                return bytes(data)
            ch = string[idx]
            idx += 1
            if ch in lookup and lookup[ch] < 0x55:
                working_u32 = (working_u32 * BASE + lookup[ch]) & 0xFFFFFFFF
                char_idx += 1
                if char_idx == 5:
                    break
        b0 = (working_u32 >> 24) & 0xFF
        b1 = (working_u32 >> 16) & 0xFF
        b2 = (working_u32 >> 8) & 0xFF
        b3 = working_u32 & 0xFF
        data.extend([b0, b1, b2, b3])
        if idx >= size:
            return bytes(data)


def mirror_bytes(data: bytes) -> bytes:
    # reverse the bits of each byte (76543210 to 01234567)
    # credit to InflamedSebi
    data = bytes(((b & 1) << 7) | ((b & 2) << 5) | ((b & 4) << 3) | ((b & 8) << 1) |
                 ((b & 16) >> 1) | ((b & 32) >> 3) | ((b & 64) >> 5) | ((b & 128) >> 7)
                 for b in data)
    return data


serial = '@Ugy3L+2}TYgOyvyviz?KiBDJYGs9dOW2m'

# Decoding pipeline, don't touch
serial = serial[2:] # Important, remove the @U, don't touch
data = b85_decode(serial) # Decode base85 with custom alphabet in big endian
data = mirror_bytes(data) # Mirror each bytes
print(''.join(format(byte, '08b') for byte in data)) # print bitstream
