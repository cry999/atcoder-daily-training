INF = 10**18

N, Q = map(int, input().split())
L = [INF] + list(map(int, input().split()))
R = list(map(int, input().split())) + [INF]

# suffix_l[i] := i より右で最小の L のあたい
suffix_l = [INF] * (N + 1)
for i in range(N - 1, -1, -1):
    suffix_l[i] = min(suffix_l[i + 1], L[i])

# prefix_r[i] := i より左で最小の R のあたい
prefix_r = [INF] * (N + 1)
for i in range(N):
    prefix_r[i + 1] = min(prefix_r[i], R[i])


for _ in range(Q):
    s, t = map(int, input().split())
    s -= 1
    t -= 1
    if s > t:  # 左に移動する
        ans = min(L[s], suffix_l[s + 1] + R[s])
    else:  # 右に移動する
        ans = min(R[s], prefix_r[s] + L[s])

    print(ans)
