# >>> atcoder-stat >>>
# started_at  = 2026-09-16T01:27:48+09:00
# solved_at   = 2026-09-16T02:11:55+09:00
# duration_ms = 2647456
# target_ms   = 900000
# <<< atcoder-stat <<<
N, M = map(int, input().split())

recruitments = []
for _ in range(N):
    day, price = map(int, input().split())
    recruitments.append((price, day))
recruitments.sort()

ans = 0
for d in range(M):
    while recruitments:
        _, day = recruitments[-1]
        if d + day <= M:
            break
        else:
            recruitments.pop()

    if not recruitments:
        break

    price, day = recruitments.pop()
    print(f"[DEBUG] {d=}, {price=}, {day=}")
    ans += price

print(ans)
