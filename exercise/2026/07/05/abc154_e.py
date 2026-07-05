# >>> atcoder-stat >>>
# started_at  = 2026-07-05T09:22:55+09:00
# <<< atcoder-stat <<<
N = input()
L = len(N)
K = int(input())

# dp[i][k][f] := i 桁目までの数字を決めて、0 以外の数字の使用回数が k で、N 以下かどうかが f な場合の数
dp = [[[0] * 2 for _ in range(K + 1)] for _ in range(L + 1)]
dp[0][0][0] = 1

# 0 以外の使用状況を確認する bit mask
for i in range(L):
    n = int(N[i])
    for k in range(K + 1):  # i 桁目までの数字の使用回数
        for less in range(2):  # i 桁目までが N より小さいかどうか
            # i 桁目までですでに N より小さいなら、何を使ってもいい。
            # そうでないなら、N の i 桁目の数字以下しか使えない。
            stop = 9 if less else n
            for d in range(stop + 1):  # i+1 桁目候補
                if k == 0 and d == 0:
                    nk = 0
                elif k == K and d != 0:
                    # K 回以上 0 以外の数字を使うことはできない
                    continue
                elif d == 0:
                    # 0 以外の数字を使わない場合は、使用回数は変わらない
                    nk = k
                else:
                    nk = k + 1
                nless = less or (d < n)
                dp[i + 1][nk][nless] += dp[i][k][less]

print(sum(dp[L][K]))
