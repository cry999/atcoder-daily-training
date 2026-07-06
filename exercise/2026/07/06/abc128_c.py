# >>> atcoder-stat >>>
# started_at  = 2026-07-06T16:09:24+09:00
# <<< atcoder-stat <<<
n, m = map(int, input().split())
light_requirements = []
for _ in range(m):
    _, *s = map(int, input().split())
    light_requirements.append(s)

(*p,) = map(int, input().split())

ans = 0
for bit in range(1 << n):
    for i in range(m):
        on = 0
        for si in light_requirements[i]:
            if bit & (1 << (si - 1)):
                on = 1 - on
        if on != p[i]:
            break
    else:
        ans += 1
print(ans)
