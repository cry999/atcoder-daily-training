N = int(input())
S = input()


# diff: 現在までの「A の出現回数 - B の出現回数」
# [-N, N] の範囲の値を取るため、配列の添字として使えるように +N で補正する
diff = 0 + N

# counter[d] := 現在より過去の diff が d だった回数。
# つまり、「A の出現回数 - B の出現回数」が d-N (N は補正分) だった prefix の個数。
counter = [0] * (2 * N + 1)

# 空の prefix をカウントしておく。
counter[diff] += 1


# sum_less: 過去の diff のうち、現在の diff より小さいものの個数
# diff は +-1 ずつしか変化しない。
# A が出現すると diff+1 になるので、counter[diff] 分だけ増える
# B が出現すると diff-1 になるので、counter[diff-1] 分だけ減る
sum_less = 0
ans = 0

for s in S:
    if s == "A":
        # diff+1 になるので、diff 以下の個数を答えに足し合わせたい。
        sum_less += counter[diff]
        diff += 1
    elif s == "B":
        # diff-1 になるので、diff-2 以下の個数を答えから除きたい。
        diff -= 1
        sum_less -= counter[diff]

    # 答えに現在の diff より小さい diff の個数を足し合わせておく。
    ans += sum_less

    # 次以降のループように現在の diff をカウントしておく
    counter[diff] += 1

print(ans)
