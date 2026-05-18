MOD = 998244353

X1, X2, X3 = map(int, input().split())

max_n = 2 * max(X1, X2, X3) + 1
inv = [0] * (max_n + 1)
inv[1] = 1
for i in range(2, max_n + 1):
    inv[i] = MOD - (MOD // i) * inv[MOD % i] % MOD


ans = 0
comb_choice_1 = 1  # 1 を入れる隙間の選び方
comb_put_1 = 1  # 1 を選んだ隙間に入れる場合の数
comb_put_3 = 1  # 3 を残りの隙間に入れる
for i in range(1, X2 + 1):
    comb_put_3 *= X3 + i
    comb_put_3 *= inv[i]
    comb_put_3 %= MOD

for n1 in range(1, min(X1, X2) + 1):
    # n1: 1 を入れる 2 の隙間の数
    # n3: 3 を入れる 2 の隙間の数
    n3 = X2 + 1 - n1

    comb_choice_1 *= X2 + 1 - (n1 - 1)
    comb_choice_1 *= inv[n1]
    comb_choice_1 %= MOD

    comb_put_3 *= n3
    comb_put_3 *= inv[X3 + n3]
    comb_put_3 %= MOD

    ans += comb_choice_1 * comb_put_1 * comb_put_3
    ans %= MOD

    comb_put_1 *= X1 - n1
    comb_put_1 *= inv[n1]
    comb_put_1 %= MOD

print(ans)
