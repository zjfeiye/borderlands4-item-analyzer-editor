import { b85Decode } from './lib/b85.js';

//console.log(b85Decode("28$(xAmkC4psDo2eQFg+T9rU~UrPW")); // just to show it runs

for (let i of all_smg) {
    console.log(b85Decode(i));
}

for (let i of all_pistols) {
    console.log(b85Decode(i));
}

var levels = [
 [1, "@Ugd_t@FcA=8^mI^IRH1&NdZON-VxdwZ00"],
 [2, "@Ugd_t@FcJ`9^mI^IRH1&NdZON-VxdwZ00"],
 [3, "@Ugd_t@FcT1A^mI^IRH1&NdZON-VxdwZ00"],
 [4, "@Ugd_t@Fcc7B^mI^IRH1&NdZON-VxdwZ00"],
 [5, "@Ugd_t@FclDC^mI^IRH1&NdZON-VxdwZ00"],
 [6, "@Ugd_t@FcuJD^mI^IRH1&NdZON-VxdwZ00"],
 [7, "@Ugd_t@Fc%PE^mI^IRH1&NdZON-VxdwZ00"],
 [8, "@Ugd_t@Fc=VF^mI^IRH1&NdZON-VxdwZ00"],
 [9, "@Ugd_t@Fc}bG^mI^IRH1&NdZON-VxdwZ00"],
 [10, "@Ugd_t@Fd7hH^mI^IRH1&NdZON-VxdwZ00"],
 [11, "@Ugd_t@FdGnI^mI^IRH1&NdZON-VxdwZ00"],
 [12, "@Ugd_t@FdPtJ^mI^IRH1&NdZON-VxdwZ00"],
 [13, "@Ugd_t@FdYzK^mI^IRH1&NdZON-VxdwZ00"],
 [14, "@Ugd_t@Fdh(L^mI^IRH1&NdZON-VxdwZ00"],
 [15, "@Ugd_t@Fdq<M^mI^IRH1&NdZON-VxdwZ00"],
 [16, "@Ugd_t@Ffb5d^mI^IRH1&NdZON-VxdwZ00"],
 [17, "@Ugd_t@FfkBe^mI^IRH1&NdZON-VxdwZ00"],
 [18, "@Ugd_t@FftHf^mI^IRH1&NdZON-VxdwZ00"],
 [19, "@Ugd_t@Ff$Ng^mI^IRH1&NdZON-VxdwZ00"],
 [20, "@Ugd_t@Ff<Th^mI^IRH1&NdZON-VxdwZ00"],
 [21, "@Ugd_t@Ff/Zi^mI^IRH1&NdZON-VxdwZ00"],
 [22, "@Ugd_t@Fg6fj^mI^IRH1&NdZON-VxdwZ00"],
 [23, "@Ugd_t@FgFlk^mI^IRH1&NdZON-VxdwZ00"],
 [24, "@Ugd_t@FgOrl^mI^IRH1&NdZON-VxdwZ00"],
 [25, "@Ugd_t@FgXxm^mI^IRH1&NdZON-VxdwZ00"],
 [26, "@Ugd_t@Fgg%n^mI^IRH1&NdZON-VxdwZ00"],
 [27, "@Ugd_t@Fgp-o^mI^IRH1&NdZON-VxdwZ00"],
 [28, "@Ugd_t@Fgy@p^mI^IRH1&NdZON-VxdwZ00"],
 [29, "@Ugd_t@Fg*}q^mI^IRH1&NdZON-VxdwZ00"],
 [30, "@Ugd_t@Fg_4r^mI^IRH1&NdZON-VxdwZ00"],
 [31, "@Ugd_t@Fh3As^mI^IRH1&NdZON-VxdwZ00"],
 [32, "@Ugd_t@Fi;R-^mI^IRH1&NdZON-VxdwZ00"],
 [33, "@Ugd_t@Fi{X;^mI^IRH1&NdZON-VxdwZ00"],
 [34, "@Ugd_t@Fj5d<^mI^IRH1&NdZON-VxdwZ00"],
 [35, "@Ugd_t@FjEj=^mI^IRH1&NdZON-VxdwZ00"],
 [36, "@Ugd_t@FjNp>^mI^IRH1&NdZON-VxdwZ00"],
 [37, "@Ugd_t@FjWv?^mI^IRH1&NdZON-VxdwZ00"],
 [38, "@Ugd_t@Fjf#@^mI^IRH1&NdZON-VxdwZ00"],
 [39, "@Ugd_t@Fjo*^^mI^IRH1&NdZON-VxdwZ00"],
 [40, "@Ugd_t@Fjx>_^mI^IRH1&NdZON-VxdwZ00"],
 [41, "@Ugd_t@Fj){`^mI^IRH1&NdZON-VxdwZ00"],
 [42, "@Ugd_t@Fj^2{^mI^IRH1&NdZON-VxdwZ00"],
 [43, "@Ugd_t@Fk28/^mI^IRH1&NdZON-VxdwZ00"],
 [44, "@Ugd_t@FkBE}^mI^IRH1&NdZON-VxdwZ00"],
 [45, "@Ugd_t@FkKK~^mI^IRH1&NdZON-VxdwZ00"],
 [46, "@Ugd_t@FkTR0^mI^IRH1&NdZON-VxdwZ00"],
 [47, "@Ugd_t@FkcX1^mI^IRH1&NdZON-VxdwZ00"],
 [48, "@Ugd_t@FmMoI^mI^IRH1&NdZON-VxdwZ00"],
 [49, "@Ugd_t@FmVuJ^mI^IRH1&NdZON-VxdwZ00"],
 [50, "@Ugd_t@Fme!K^mI^IRH1&NdZON-VxdwZ00"],
];

for (let i of levels) {
    var hex = b85Decode(i[1]);
    console.log(i[0], hex, hex[10] + hex[11]);
}


var hex = b85Decode("@Ugb)KvFme!KxE9c8RG}8ts6;(#9_mwXP<c?VP%#k");
console.log(hex, hex[12] + hex[13]);
var hex = b85Decode("@UgwSAs2}TYgOz#USjp~P5)S(jfsJ*DNsIaI@g+bLpr9!Pj^+J_H00");
console.log(hex, hex[12] + hex[13]);

