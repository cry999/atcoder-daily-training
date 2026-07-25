# >>> atcoder-stat >>>
# started_at  = 2026-07-23T10:47:02+09:00
# solved_at   = 2026-07-23T10:57:39+09:00
# duration_ms = 637580
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
T = int(input())

for _ in range(T):
    N = int(input())
    S = input()

    danger = set()
    for i, s in enumerate(S):
        if s == "1":
            danger.add(i + 1)

    dp = [False] * (1 << N)
    dp[0] = True
    for s in range(1 << N):
        if not dp[s]:
            continue
        for i in range(N):
            if s & (1 << i):
                continue
            ns = s | (1 << i)
            if ns in danger:
                continue
            dp[ns] = True
    print(f"[DEBUG] {dp=}")

    ALL = (1 << N) - 1
    print("Yes" if dp[ALL] else "No")
