function hexToInt(hex) {
    if (hex === '0') return 0;
    if (hex === '1') return 1;
    if (hex === '2') return 2;
    if (hex === '3') return 3;
    if (hex === '4') return 4;
    if (hex === '5') return 5;
    if (hex === '6') return 6;
    if (hex === '7') return 7;
    if (hex === '8') return 8;
    if (hex === '9') return 9;
    if (hex === 'a' || hex === 'A') return 10;
    if (hex === 'b' || hex === 'B') return 11;
    if (hex === 'c' || hex === 'C') return 12;
    if (hex === 'd' || hex === 'D') return 13;
    if (hex === 'e' || hex === 'E') return 14;
    if (hex === 'f' || hex === 'F') return 15;
    return null;
}

function intToHex(int) {
    if (int === 0) return '0';
    if (int === 1) return '1';
    if (int === 2) return '2';
    if (int === 3) return '3';
    if (int === 4) return '4';
    if (int === 5) return '5';
    if (int === 6) return '6';
    if (int === 7) return '7';
    if (int === 8) return '8';
    if (int === 9) return '9';
    if (int === 10) return 'a';
    if (int === 11) return 'b';
    if (int === 12) return 'c';
    if (int === 13) return 'd';
    if (int === 14) return 'e';
    if (int === 15) return 'f';
    return null;
}

export { hexToInt, intToHex };
