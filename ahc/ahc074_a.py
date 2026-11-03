import base64
import json
import math
import random
import sys
import time
import zlib

# 4 窓・8 枚の全重ね順を探索して得た最短操作の方策。
# 再生成方法と探索コードは ahc/ahc074/README.md を参照。
DATA = (
    "c-o~{+m0M35dD{VCZmRip~<hT=D~_rmL<!!Hv1Aq`S(y1P#3Ca$H~6zG}k(HIUM-=^7GUC`|I2HKQF((TsH5wi@R*~um1D(5B_b~"
    "=v(7<#joqN^<A&m%iUeRynXuo_4WIEUF5fLO+KgH)gR$j{LPsydn{XkA2FAB*e#pC-P(_s(k<I9F~rzrm5|EPP)+;s_WAV<(7kNV"
    "yWn;gU2-><@9sr>yREk5I_6ftV{H$uW%T;ll4~!Fp_Va%X3?sC&VujAW??ViE7uXS1;#|NS8l5$wN4Vd=WbtAWBBeIxo0T&81M4p"
    "jl5t-tNHFpwcwbjP$ae2*q`r?KBHM)wL~{|<I#~V-VO9LYxs=sp4G|&8Mf3^`uXGA*FXM(RI1}&^1XQxjEXJ<7mC~K0=r8vxMl$B"
    "xwi$y&_qL%TIAjWHrn88b1(OXO)nAp631!>G#A6X*sSr}YEEnShM9fJ3bq;N_qBaYSwZ8J4*3or;LPsJGfyf%o_TTg;q;)tiD})N"
    "XTCH&dFn^oi>E%cJ$ULr+k4Y@6-64U*gB84%N~ZW>Tk5EG`nKM7`FC-fP-(tuqU_Q(-Y}%ej5(h24ZLp9P9iD*y$%MKX9};Z9DKm"
    "K=VT#QUM<wfC_tuprVYy1qA3S?0^8zxT<jSDC*#enCVc72<gDgcmN>W5jsayB&;%GgTabDSlytFA)=VTnj0bFF<B6?$n0^#i7Y1Q"
    "HUz?Af<8kC6q8}OC_<K1vC^aO@l3sZ>+T{N*qeK6AAG=?-Ea|yx+0DM!|O*Z;~UJFK@btBACyw9$MM9%Vj56ZR+)UVG70C9frk^v"
    "N*RhQ44TjcVNio61%nPa5rn`j8MzlC%e_R&7ob3J8syXDgp?hxsF8e_ry1d6($%P7e`yiwX@p5fumllQyD0DIBlb>;UAO(9)a!Ln"
    "RN_I1JEJ8<XpoVfvX6>qrs{!kz<y$HPGq<|K_DW7p2=k_>nP=*=%w+`bMZ7?b1^p^LsEK1ZY^{VXgJ$6oGltY1YgCLc4hc~+RrFh"
    "+TO!@lbi(|$)MoKO2v0+gU%=3Wp1aOA+Cy8iyv^UGJIj%X}M-wZh5PZGq%mccII`HXtPDMEZZxf@<hHf+b7S)!L4Ap$+Lx-EP1v#"
    "`W^yepOJVb)60j6u5AWqpV?gf#Eu7+=lXacn|lnpT=>5!4(;S@#*ArWSx$*E=wEPSae^KNy-<OkBsuw;on%89&cn=7$y_3v`dEo$"
    "QpQRao0@nP#I_nXq_C}n4H0ZBU_<_z>Jdc=!rOUFP4S4Tgks9YiWSr*Nz9;fQ2M|Vp^Z|kP%%ASOTRAQtF80gAOQ~}^4ZA&>*n?3"
    "XmfN~Jz(FV-uM5mbYW0F;odzuqF++FZOTf(uxi!>yl;$v16sa&MZm#{2+Z_h$Mr}Z&&ikEF35M1(?Vo1Fw1+Y$KEV;?&P#M>`y&;"
    "!i`xUvdW(Bfqvwo$|D{o5<W~4J|2<q;kZT@BG0yc-(>BE$;S`@?tY#?<b8H>Pxn*V&SO|h)fpElRnf^OQZ@3#kKuXQ!OuYJD8Z9Z"
    "A0>F&oha>WEA2DYF{~!O94{^2o!#vk7qCYa&-li^;K2+|Ii5Y5c=cAY=vDqQ;`xJ!SMMN!T^Mjje&zXvGMM~^pcsSBOV6wY7<(u<"
    "oJ5aDBzkB#oJtQ3hp=?(#>M(^O^??W31+^wh{A?D%n6uO9^EByq7A0cJOguf7hP|nle*<ibW(R7H-LUJ9A_s(l5rs|66Qqts>4r-"
    "L%-^L45eG0=}~9Cx2Q|?;n*7$Mdkd0p_G(>l9YN9P?CBl;7|^tfz8?XY>(2#yk}3{q3_vJcTCaosQin0*@o?mD~M+$e=HA&>;^UX"
    "H#+;uI>m>+vMTW*f>MO|Am!n#duyAp-dka>LI)s40hiX|18I&k7w6(tfxvjrS(s@*#a!Yb)XXKMh-R)Rb>K`Zb)ut+pC>wnBpT;A"
    "4E9v;>>1bdXb>D-@B)r5cmYQjynr*R<o?gUhm8T%"
)


def main():
    started = time.process_time()
    read = sys.stdin.readline
    line = read()
    if not line or line.strip() == "-1":
        return
    n, k, p, r = map(int, line.split())
    products = [read().strip() for _ in range(p)]
    data = json.loads(zlib.decompress(base64.b85decode(DATA)))
    patterns = data["patterns"]
    policy = data["policy"]
    gradient = data["gradient"]

    # 未来の注文は読まず、既知の商品一覧だけで窓の組と色反転を選ぶ。
    columns = [sum((s[j] == "1") << i for i, s in enumerate(products))
               for j in range(n)]
    full = (1 << p) - 1
    rng = random.Random(74)
    if "--baseline" in sys.argv:
        return simple(n, k, r, products, read)
    groups = [list(range(j, j + 4)) for j in range(0, n, 4)]

    def evaluate(cols):
        masks = [full]
        for col in cols:
            bit = columns[col]
            masks = [x & ~bit for x in masks] + [x & bit for x in masks]
        counts = [x.bit_count() for x in masks]
        score, flip = min((sum(counts[t] * gradient[t ^ x]
                               for t in range(16)), x) for x in range(16))
        return score, flip

    values = [evaluate(g) for g in groups]
    best = sum(x[0] for x in values)
    best_groups = [g[:] for g in groups]
    best_flips = [x[1] for x in values]
    for it in range(12000):
        if it % 64 == 0 and time.process_time() - started >= 0.60:
            break
        a, b = rng.sample(range(16), 2)
        x, y = rng.randrange(4), rng.randrange(4)
        groups[a][x], groups[b][y] = groups[b][y], groups[a][x]
        va, vb = evaluate(groups[a]), evaluate(groups[b])
        delta = va[0] + vb[0] - values[a][0] - values[b][0]
        temp = 4.0 * (0.05 / 4.0) ** (it / 12000)
        if delta <= 0 or rng.random() < math.exp(-delta / temp):
            values[a], values[b] = va, vb
            score = sum(v[0] for v in values)
            if score < best:
                best = score
                best_groups = [g[:] for g in groups]
                best_flips = [v[1] for v in values]
        else:
            groups[a][x], groups[b][y] = groups[b][y], groups[a][x]
    groups, flips = best_groups, best_flips

    codes = [[sum((s[col] == "1") << j for j, col in enumerate(g)) ^ flip
              for g, flip in zip(groups, flips)] for s in products]
    states = []
    labels = []
    sheets = []
    for i, (g, flip) in enumerate(zip(groups, flips)):
        counts = [0] * 16
        for code in codes:
            counts[code[i]] += 1
        state = min(range(len(policy)), key=lambda s:
                    sum(counts[t] * len(policy[s][t][1]) for t in range(16)))
        states.append(state)
        order = data["orders"][state]
        inverse = [0] * 8
        for j, original in enumerate(order):
            inverse[original] = j
            sheet = ["."] * n
            for bit, col in enumerate(g):
                color = patterns[original][bit]
                if color != ".":
                    sheet[col] = str(int(color) ^ (flip >> bit & 1))
            sheets.append("".join(sheet))
        labels.append(inverse)
    # 残りの紙は全て穴にする。
    sheets += ["." * n] * (k - len(sheets))
    print("\n".join(sheets), flush=True)
    for _ in range(r):
        line = read()
        if not line or line.strip() == "-1":
            return
        target = int(line)
        moves = []
        for i, code in enumerate(codes[target]):
            states[i], actions = policy[states[i]][code]
            offset = i * 8
            moves.extend((offset + labels[i][action // 8], offset + action % 8)
                         for action in actions)
        print(str(len(moves)) + "".join(f"\n{a} {d}" for a, d in moves),
              flush=True)


def simple(n, k, r, products, read):
    if k < 2 * n:
        return
    sheets = []
    for j in range(n):
        for color in "01":
            sheets.append("." * j + color + "." * (n - j - 1))
    print("\n".join(sheets + ["." * n] * (k - 2 * n)), flush=True)
    current = [0] * n
    for _ in range(r):
        line = read()
        if not line or line.strip() == "-1":
            return
        target = products[int(line)]
        moves = []
        for j, c in enumerate(target):
            color = int(c)
            if current[j] != color:
                moves.append((2 * j + current[j], 2 * j + 1))
                current[j] = color
        print(str(len(moves)) + "".join(f"\n{a} {d}" for a, d in moves),
              flush=True)


if __name__ == "__main__":
    main()
