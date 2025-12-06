import bisect


H, W, N = map(int, input().split())
AB = [tuple(map(int, input().split())) for _ in range(N)]

*shrinked_rows, = sorted(set(A for A, _ in AB))
*shrinked_cols, = sorted(set(B for _, B in AB))


for A, B in AB:
    h = bisect.bisect_left(shrinked_rows, A)
    w = bisect.bisect_left(shrinked_cols, B)

    print(h+1, w+1)
