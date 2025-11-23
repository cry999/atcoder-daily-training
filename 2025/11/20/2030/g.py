N = int(input())
S = input()

# z[i] := 左から i 番目の '0' の S でのインデックス
z = []
for i, c in enumerate(S):
    if c != '0':
        continue
    z.append(i)
# print('z:', z)

if not z:
    # '0' が存在しない場合は、操作不要
    print(0)
else:
    # o[i] := 左から i 番目までの '1' の個数
    o = [0] * N
    o[0] = 1 if S[0] == '1' else 0
    for i in range(1, N):
        o[i] = o[i-1] + (1 if S[i] == '1' else 0)
    # print('o:', o)
    print(sum(min(o[zi], o[-1]-o[zi]) for zi in z))

    # # sl[z[i]] := 左から '0' を追い出すための操作回数
    # #          :=  (z[i] 未満の '1' の個数) + sl[z[i-1]]
    # sl = [0] * N
    # sl[z[0]] = o[z[0]]
    # for i in range(1, len(z)):
    #     sl[z[i]] = o[z[i]] + sl[z[i-1]]
    #
    # # print('sl:', sl)
    # # sr[z[i]] := 右から '0' を追い出すための操作回数
    # #          := (z[i]+1 以上の '1' の個数) + sr[z[i+1]]
    # sr = [0] * N
    # # o[-1] は左端から右端までの '1' の個数 = '1' の総数
    # sr[z[-1]] = (o[-1] - o[z[-1]])
    # for i in range(1, len(z)):
    #     sr[z[-i-1]] = (o[-1] - o[z[-i-1]]) + sr[z[-i]]
    # # print('sr:', sr)
    #
    # # 各 '0' は左右の操作回数の少ない方から追い出す。
    # # それぞれの最大操作回数の和が全体の操作回数。
    # lo, ro = 0, 0
    # for zi in z:
    #     if sl[zi] < sr[zi]:
    #         lo = sl[zi]
    #     else:
    #         ro = sr[zi]
    #         break
    #
    # print(lo+ro)
