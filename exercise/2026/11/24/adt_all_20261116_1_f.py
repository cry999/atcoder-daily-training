# >>> atcoder-stat >>>
# started_at  = 2026-11-24T07:10:22+09:00
# solved_at   = 2026-11-24T07:17:51+09:00
# duration_ms = 449453
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, M = map(int, input().split())

DIRS = [(0, 0), (1, 0), (0, 1), (1, 1)]

blocks: dict[int, set[int]] = {}
ans = 0
for _ in range(M):
    r0, c0 = map(int, input().split())
    if all(r0 + dr not in blocks or c0 + dc not in blocks[r0 + dr] for dr, dc in DIRS):
        ans += 1
        for dr, dc in DIRS:
            blocks.setdefault(r0 + dr, {c0 + dc}).add(c0 + dc)
    print(f"[DEBUG] {blocks=}")

print(ans)
