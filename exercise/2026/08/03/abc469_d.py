# >>> atcoder-stat >>>
# started_at  = 2026-08-03T09:07:40+09:00
# solved_at   = 2026-08-03T09:14:14+09:00
# duration_ms = 394595
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

N, M = map(int, input().split())
pairs = [tuple(map(int, input().split())) for _ in range(M)]

ans = set()

# pairs[0] の a, b のどちらかは (x, y) に必ず含まれる。
# 含まれる方を固定して探索する。
for fixed in pairs[0]:
    # fixed を含むペアの相方を探す。

    partner = set(range(1, N + 1))
    for a, b in pairs:
        if fixed == a or fixed == b:
            # fixed を含むペアは相方を制限しないので無視
            continue

        # fixed を含まないペアは相方を a, b のいずれかを含むように制限する
        partner &= {a, b}

    ans |= {(min(fixed, p), max(fixed, p)) for p in partner if p != fixed}

print(len(ans))
