N, T = map(int, input().split())

hist = {0: N}
scores = [0] * (N + 1)

ans = 1
for _ in range(T):
    A, B = map(int, input().split())
    hist[scores[A]] -= 1
    if hist[scores[A]] == 0:
        ans -= 1

    scores[A] += B
    if hist.get(scores[A], 0) == 0:
        ans += 1
        hist[scores[A]] = 0
    hist[scores[A]] += 1

    print(ans)
