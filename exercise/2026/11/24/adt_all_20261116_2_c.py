# >>> atcoder-stat >>>
# started_at  = 2026-11-24T09:54:24+09:00
# solved_at   = 2026-11-24T09:57:41+09:00
# duration_ms = 197574
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
S = input()
T: list[str] = []

can_place_o = True
for s in S:
    if s == "#":
        can_place_o = True
        T.append(s)
    elif can_place_o:
        can_place_o = False
        T.append("o")
    else:
        T.append(".")
print("".join(T))
