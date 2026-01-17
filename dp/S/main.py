from atcoder.modint import Modint, ModContext

K = int(input())
D = int(input())

MOD = 10**9 + 7

digit_length = len(str(K))

with ModContext(MOD):
    # dp[k][d] := 10^(k+1) 未満の数字で桁の総和を D で割ったあまりが d である数字の個数
    dp = [[Modint(0) for _ in range(D)] for _ in range(digit_length + 1)]
    for d in range(10):
        dp[0][d % D] += Modint(1)

    for k in range(digit_length):
        for d in range(D):
            for n in range(10):
                # 先頭に n を追加する
                dp[k + 1][d % D] += dp[k][(d - n) % D]

    # 先頭の桁から計算していく
    k = digit_length - 1
    offset = 0
    ans = Modint(0)
    while k >= 0:
        # k 桁目の数字を求める。
        kth_digit = (K // (10**k)) % 10
        old = ans

        if k == 0:
            for d in range(kth_digit):
                ans += (d + offset) % D == 0
        else:
            for d in range(kth_digit):
                ans += dp[k - 1][(D - offset - d) % D]

        offset += kth_digit
        offset %= D
        k -= 1

    ans -= 1  # 0 を引く
    if offset % D == 0:
        ans += 1
    print(ans.val())
