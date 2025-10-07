#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

typedef unsigned char byte;
typedef unsigned short ushort;
typedef unsigned int uint;
typedef long long longlong;
typedef unsigned long long ulonglong;

static byte b85_reverse_lookup[256];
static char b85_reverse_lookup_initalized = '\0';
static char DAT_15117f6ec;
static char DAT_15117f69f;

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

  iVar4 = (int)(intptr_t)data;
  if (b85_reverse_lookup_initalized == '\0') {
    lVar2 = 0;
    do {
      cVar1 = (char)lVar2;
      b85_reverse_lookup
      [(byte)"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~"
             [lVar2]] = cVar1;
      b85_reverse_lookup
      [(byte)"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~"
             [lVar2 + 1]] = cVar1 + '\x01';
      b85_reverse_lookup
      [(byte)"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~"
             [lVar2 + 2]] = cVar1 + '\x02';
      b85_reverse_lookup
      [(byte)"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~"
             [lVar2 + 3]] = cVar1 + '\x03';
      b85_reverse_lookup
      [(byte)"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~"
             [lVar2 + 4]] = cVar1 + '\x04';
      lVar2 = lVar2 + 5;
    } while (lVar2 != 0x55);
    DAT_15117f6ec = DAT_15117f69f;
    b85_reverse_lookup_initalized = '\x01';
  }
  if (size == 0) {
b85_decode_quit:
    return (int)((intptr_t)data - iVar4);
  }
  uVar6 = 0;
LAB_1429773c9:
  working_u32 = 0;
  char_idx = 0;
  idx = uVar6;
  do {
    uVar6 = idx + 1;
    if ((-1 < (longlong)string[idx]) && ((byte)b85_reverse_lookup[(byte)string[idx]] < 0x56)) {
      working_u32 = working_u32 * 0x55 + (uint)(byte)b85_reverse_lookup[(byte)string[idx]];
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
  } while( 1 );
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

  iVar2 = (int)(intptr_t)str;
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
      str[1] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~"
               [(ulonglong)uVar4 / 0x95eed];
      str[2] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~"
               [(ulonglong)uVar5 / 0x1c39];
      str[3] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~"
               [uVar6 / 0x55];
      str[4] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~"
               [uVar6 % 0x55];
      str = str + 5;
      working_u32 = working_u32 - 1;
    } while (working_u32 != 0);
  }
  if (extra_bytes != 0) {
    last_u32 = (uint)(byte)*(uint *)data;
    if (extra_bytes != 1) {
      uVar1 = ((uint)(byte)*(uint *)data << 8) | *(byte *)((longlong)data + 1);
      last_u32 = (uint)uVar1;
      if (extra_bytes != 2) {
        last_u32 = (uVar1 << 8) | *(byte *)((longlong)data + 2);
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
      str[2] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~"
               [(ulonglong)working_u32 / 0x1c39];
      if (extra_bytes == 3) {
        str[3] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{/}~"
                 [(working_u32 % 0x1c39) / 0x55];
        str = str + 4;
      }
      else {
        str = str + 3;
      }
    }
  }
  return (int)((intptr_t)str - iVar2);
}

int main(int argc, char *argv[])
{
  if (argc != 3) {
    fprintf(stderr, "Usage: %s --encode|--decode <string>\n", argv[0]);
    return 1;
  }

  if (strcmp(argv[1], "--encode") == 0) {
    const char *hex = argv[2];
    int hex_len = strlen(hex);
    if (hex_len % 2 != 0) {
      fprintf(stderr, "Hex string must have even length\n");
      return 1;
    }
    int data_len = hex_len / 2;
    byte *data = malloc(data_len);
    for (int i = 0; i < data_len; i++) {
      sscanf(hex + i * 2, "%2hhx", &data[i]);
    }
    char *output = malloc(data_len * 2);
    int out_len = b85_encode(data, data_len, output);
    fwrite(output, 1, out_len, stdout);
    printf("\n");
    free(data);
    free(output);
  }
  else if (strcmp(argv[1], "--decode") == 0) {
    const char *b85 = argv[2];
    int b85_len = strlen(b85);
    byte *data = malloc(b85_len);
    int data_len = b85_decode((char *)b85, b85_len, data);
    for (int i = 0; i < data_len; i++) {
      printf("%02x", data[i]);
    }
    printf("\n");
    free(data);
  }
  else {
    fprintf(stderr, "First argument must be --encode or --decode\n");
    return 1;
  }

  return 0;
}

