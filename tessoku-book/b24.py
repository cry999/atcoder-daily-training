N = int(input())
BOXES = [list(map(int, input().split())) for _ in range(N)]
# まずは幅でソート、幅が同じなら高さが高い順にソート
# こうすることで、幅が同じ箱は積み重ねられないようにできる
BOXES.sort(key=lambda x: (x[0], -x[1]))
# print(BOXES)

# dp[i] := Yi が末尾の最長列
dp = [0] * N
# L[i] := i 重のはこの最小 Yi
L = [float('inf')] * (N + 1)
L[0] = 0

max_boxes = 0
for i in range(N):
    # Yi 未満の高さで最大重の重箱数を二分探索
    lo, hi = 0, N
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if L[mid] < BOXES[i][1]:
            lo = mid
        else:
            hi = mid - 1

    dp[i] = lo + 1
    L[dp[i]] = min(L[dp[i]], BOXES[i][1])
    max_boxes = max(max_boxes, dp[i])

print(max_boxes)
