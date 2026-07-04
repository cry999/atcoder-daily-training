# >>> atcoder-stat >>>
# started_at  = 2026-07-04T20:59:46+09:00
# <<< atcoder-stat <<<

T = int(input())

for _ in range(T):
    X, Y, K = map(int, input().split())

    op = 0
    while X != Y:
        if X > Y:
            X //= K
        else:
            Y //= K
        op += 1

    print(op)
