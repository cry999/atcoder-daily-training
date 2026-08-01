N, K = map(int, input().split())
S = input()

# wins[i] := 文字列 S の先頭から i 文字目までの勝利数
wins = [0] * (N + 1)
for i in range(N):
    wins[i + 1] = wins[i] + (S[i] == "o")


def check(p: float):
    """p 以上の勝率を達成できるかをチェックする"""

    min_w = float("inf")
    left = 0
    for right in range(1, N + 1):
        while left < right and wins[left] <= wins[right] - K:
            w = wins[left] - p * left
            min_w = min(min_w, w)
            left += 1

        if min_w <= wins[right] - p * right:
            return True

    return False


lo, hi = 0, 1
eps = 1e-15

while hi - lo > eps:
    mid = (lo + hi) / 2

    if check(mid):
        lo = mid
    else:
        hi = mid

print(lo)
