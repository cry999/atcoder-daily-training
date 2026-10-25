# >>> atcoder-stat >>>
# started_at  = 2026-10-24T20:54:58+09:00
# solved_at   = 2026-10-24T20:56:49+09:00
# duration_ms = 111278
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
S1 = input()
S2 = input()

if (
    S1 in ("AD", "DA")
    or S2 in ("AD", "DA")
    or any(s1 + s2 in ("AD", "DA") for s1, s2 in zip(S1, S2))
):
    print("Yes")
else:
    print("No")
