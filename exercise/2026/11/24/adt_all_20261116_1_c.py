# >>> atcoder-stat >>>
# started_at  = 2026-11-24T06:52:48+09:00
# solved_at   = 2026-11-24T06:56:54+09:00
# duration_ms = 246875
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
(*D,) = map(int, input().split())


ans = 0
for i in range(N):
    if i + 1 >= 10 and (i + 1) % 11:
        continue
    d = (i + 1) % 10
    while d <= D[i]:
        print(f"[DEBUG] {i+1=} {d=} {D[i]=}")
        ans += 1
        d = d * 10 + d
print(ans)
