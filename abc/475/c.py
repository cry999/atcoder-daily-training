from bisect import bisect_right

N, S, L = map(int, input().split())
S -= 1
(*A,) = map(int, input().split())

# 右いって折り返しと左いって折り返しを比較か。
# 累積和

prefix_right = [0] * (N - S)
prefix_left = [0] * (S + 1)

for i in range(S, N - 1):
    prefix_right[i - S + 1] = A[i] + prefix_right[i - S]

for i in range(S):
    prefix_left[i + 1] = A[S - i - 1] + prefix_left[i]

ans = 0
# 最初に右に行く場合
for i in range(S + 1, N):
    # i: 右側の到達点
    # まずは右に i 進んで S に戻ってくる。
    cost = prefix_right[i - S]
    if cost > L:
        # 行きだけで無理なら終了
        break

    cost += prefix_right[i - S]  # 戻るコスト
    if cost > L:
        # i まではいけている
        ans = max(ans, i - S)
        continue

    # ここから左に行く最高値
    j = bisect_right(prefix_left, L - cost) - 1
    ans = max(ans, i - S + j)

# 最初に左に行く場合
for i in range(S + 1):
    # i: 左側の到達点
    # まずは左に i 進んで S に戻ってくる。
    cost = prefix_left[i]
    if cost > L:
        # 行きだけで無理なら終了
        break

    cost += prefix_left[i]  # 戻るコスト
    if cost > L:
        # i まではいけている
        ans = max(ans, i)
        continue

    # ここから右に行く最高値
    bisectg_right = None
    j = bisect_right(prefix_right, L - cost) - 1
    ans = max(ans, i + j)


print(ans + 1)
