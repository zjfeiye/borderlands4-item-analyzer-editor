import {b85Decode} from "./lib/b85.js";
import {hexToBin} from "./lib/hex_to_bin.js";

let textfile = `
!!Shotgun:
jakobs:
@Ugd_t@Fk28/{3Xy\`RG}7C7u64S57ig-22~5S3jq
@Ugd_t@Fk28/pchbBRH1&NdZON-VxdwZ00

maliwan:
@UgeU_{Fk28/vL;Y!RG/*ls9{5odWjl/\`iBaGs)PE2s)Y)N8a@C
@UgeU_{Fme!KDrZn>RG}KRs6-7Hnp8{FN>oZz7*rfo9@HLGEL1K8


daedalus:
@UgdhV<Fme!Kq%_bvRG/))sC1~Bs7#GP%/V4i%/iV\`?L<6\`4Fd
@UgdhV<Fme!Kye7~(RG/*FsC1~Bs7ie*C#nwW4{8=_9I7V*


!!Rifle:
daedalus:
@Ugfs(8Fme!KJY\`U7)SwC#sYzWb4k{ID6)GHR9I74aCIS

order:
@UgggUGFme!KEIrUoR83T(3RMpk54EX5jY7pj^+Es

maliwan:
@Ugydj=2}TYg%-#mthbq*e8nviI4H?RZnu&UeYKdBj+EgCYDO4)dEmS$w5Dow



!!SMG:
deadalus:
@UgwSAs38o7oOtlEQhw6t~RHF\`+sNq6/8q}xGpxU73pjx3\`p<*Eb  --Frangible

valdof:
@UgxFw!2}TYgjHU>Riz-y3h6=q!ZE6nc4k{Gt4{8@G9cmr/

maliwan:
@Ugw$Yw2}TYgjD\`mKhbq+2p?;{9sC}rGs7=j5-9nW^4GRD


!!Sniper:
maliwan:
@Ugydj=2}TYg%=HSohbq*f64j{TLTOMXQ6o_&Q8Q6vP<v3NP@_<}P~}j=8vp
@Ugydj=2}TYgOrH(fhbmN~7ImmZ4H?RZT8V0jdWnjO>eL=oDby&\`Ez~*G5Dow
@Ugydj=2}TYgOyma&iz-y28nvjQLqAa\`Q6o_$Q8Q7Sx\`PUZ\`h&WKDu)^x00


!!Shield:
daedalus:
@Uge9B?m/&<N$pj({-Upggq}ta86u$?xk7kY-00
@Uge9B?m/)}}$pj({-Upggq}ta86u$?xk7kY-00
@Uge9B?m/)@{!o+-_NkyuCG&V#FieCf(

jakobs:
@Uge92<m/(gf!oY5zNkyuCYe2iBX))Bk0ss
@Uge92<m/)}}!bpCgL{+MNYe2iBDZzo-R{;

ripper:
@Uge8^+m/)}}!tjisNkyuCbwKf>Igx?dw*U

torgue:
@Ugr%Scm/)}}$pj({hYxyGrP>z<v^$y<8mLk2TL1

maliwan:
@Ugr$oHm/)}}!hGMLMir\`kbwKeuQ2S\`ENC5



!!Ordnance:
other:
torgue:
@Ugr$fEm/(gf!g$@FQK(LZL6t#\`K@AsLgQ/nNg8%
@Ugr$fEm/(OZ!bpmsRH#mkL7hRxLZxp2

vladof:
@Uge8pzm/)}}!e}m_IH*QVs#1>{GPDO32Gt1

maliwan:
@Ugr$%Mm/)@{!tigPK\`km$jT$;s2LS
@Ugr$%Mm/(gf!uX4zH>gE5DpHdgGIXghs4)l

ripper:
@Ugr$iFm/)}}!hFo2Kd4J}st*D


grenade:
torgue:
@Uge8>*m/(mh$pj)yh6/chq}E4sLpY)IT>t
@Uge8>*m/)@{!ffB5M^$QlbwG_;AB\`tb00


!!Enhancement:
torgue:
@Ugr%1Tm/(OZ$pj)y><xO<\`*wl~^*)+da$B^D0R

jakobs:
@Uge8Usm/(Ub!bDi0NWCv7=um@tAB\`@FD+vG

valdof:
@Uge98>m/)@{!sw5nMZIq)s8H{tp(C5cswe;

ripper:
@Uge8;)m/)}}!o*sjM!jz*=uq#Yi6(SKD*y

order:
@Ugr$rIm/)}}$pj+I?*)3)\`*wl~^*$O~Qdhi*0s

maliwan:
@Ugr$cDm/)}}!obd;N4;++Xi)E?(Ij\`}DgX

hyperion:
@Uge8Oqm/)}}!c488NWCv7Xi/lG9}O<KD+&M

cov:
@Uge8v#m/)}}!obg<MZIq)=uq#YktB6xD*y

atlas:
@Uge8s!m/)}}!pM%GMZIq)Xi)E?*(GyjD*y


!!Class:
@Ug#2fK2}TPd%(M+UiHg+!)ce%wR4Ie%XHe}7Y89$>G(1F$OaT
@Ug#2fK2__4YOd!JisGv5eP1P\`{nFbZYpkf@<KZELTP%jUvb~Mujk8lD
@Ug#2fK2}TYgOvDa4iHg+!)GE/%R6m2-Z&3LT>i$91j%J3q\`~U
@Ugr$K7m/)}}$pj)ywhWqsy3\`$1A5\`ho/I{dh>Ss{<4Jx!j)sE(d$Proq
@Ug!pHG2}TYgOqUEghx*jtRNK_LR3C#{lUk2TVNkWBDN*?Z00


!!Repkit:
vladof:
@Ugr$ZCm/(ad!o&tG>QU#TxhB?7qs~VIO9TJ

torge:
@Ugr$N8m/)}}!o<y>MLp_#G}nY0YSj5c0{{

ripper:
@Uge8dvm/(Ub!fei<M-}RPG}y!%8r1p50ss

maliwan:
@Uge8Rrm/)}}$pj+Il?htZqs~X8O{k$posZ^/C;$

order:
@Ugr$xKm/)}}!gQ;kMiuIOG}?rk+!0>lMHB!
`;

// split lines
let lines = textfile.trim().split('\n');

for (let i = 0; i < lines.length; i++) {
    // if starts with @U, decode
    if (lines[i].startsWith('@U')) {
        let serial = lines[i].trim();
        let b02 = hexToBin(b85Decode(serial));
        console.log(b02);
    } else {
        console.log(lines[i]);
    }
}
