# >>> atcoder-stat >>>
# started_at  = 2026-09-09T10:07:39+09:00
# solved_at   = 2026-09-09T10:20:16+09:00
# duration_ms = 757731
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
S = input()

cnt_0, cnt_1 = 0, 0
ans = 0
for s in S:
    if s == "0":
        cnt_1 += cnt_0
        cnt_0 = 1
    else:  # s == '1'
        cnt_0, cnt_1 = cnt_1, cnt_0
        cnt_1 += 1
    ans += cnt_1
    print(f"[DEBUG] {cnt_0=}, {cnt_1=}")

print(ans)
