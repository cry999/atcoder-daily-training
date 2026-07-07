from bisect import bisect_right

N, M = map(int, input().split())
P = [int(input()) for _ in range(N)]

# 0~2 回ダーツを放った場合の得点を全列挙。
# 3~4 回放った場合は、これを利用して二分探索する。
Q = [0]
for i in range(N):
    if P[i] <= M:
        Q.append(P[i])
    else:
        continue
    for j in range(N):
        if P[i] + P[j] <= M:
            Q.append(P[i] + P[j])
Q.sort()

ans = 0
for i, q1 in enumerate(Q):
    j = bisect_right(Q, M - q1, lo=i)
    if j < len(Q) and Q[j] + q1 <= M:
        ans = max(ans, Q[j] + q1)
    if j - 1 >= 0 and Q[j - 1] + q1 <= M:
        ans = max(ans, Q[j - 1] + q1)
print(ans)
