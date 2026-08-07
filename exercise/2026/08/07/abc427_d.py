# >>> atcoder-stat >>>
# started_at  = 2026-08-07T15:32:03+09:00
# solved_at   = 2026-08-07T15:46:03+09:00
# duration_ms = 840800
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline

T = int(input())

ans = []
for _ in range(T):
    N, M, K = map(int, input().split())
    S = input()

    g = [[] for _ in range(N)]
    for _ in range(M):
        u, v = map(int, input().split())
        g[u - 1].append(v - 1)

    dp_alice = [False] * N
    dp_bob = [False] * N

    for i in range(N):
        if S[i] == "A":
            dp_alice[i] = True
        else:
            dp_bob[i] = True

    for _ in range(K):
        for u in range(N):
            dp_bob[u] = not all(dp_alice[v] for v in g[u])
        for u in range(N):
            dp_alice[u] = not all(dp_bob[v] for v in g[u])

    if dp_alice[0]:
        ans.append("Alice")
    else:
        ans.append("Bob")

print("\n".join(ans))
