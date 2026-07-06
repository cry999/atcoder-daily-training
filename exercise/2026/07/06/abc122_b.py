# >>> atcoder-stat >>>
# started_at  = 2026-07-06T11:34:44+09:00
# solved_at   = 2026-07-06T11:37:33+09:00
# duration_ms = 169092
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
S = input()
L = len(S)

head, tail = 0, 0
ans = 0
while head < L:
    while head < L and S[head] not in "ACGT":
        head += 1

    tail = max(tail, head)
    while tail < L and S[tail] in "ACGT":
        tail += 1

    ans = max(ans, tail - head)
    head = tail

print(ans)
