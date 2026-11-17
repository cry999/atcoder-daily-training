# >>> atcoder-stat >>>
# started_at  = 2026-11-07T07:20:34+09:00
# solved_at   = 2026-11-07T07:25:47+09:00
# duration_ms = 313609
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())

bit_pos = [i for i in range(61) if N & (1 << i)]
shrink_x = [i for i in range(1 << N.bit_count())]

for s in shrink_x:
    x = 0
    for i in range(N.bit_count()):
        if s & (1 << i):
            x |= 1 << bit_pos[i]
    print(x)
