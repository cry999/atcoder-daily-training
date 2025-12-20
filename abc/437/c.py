T = int(input())

for _ in range(T):
    N = int(input())
    WP = [tuple(map(int, input().split())) for _ in range(N)]
    WP.sort(key=lambda x: x[0]+x[1], reverse=True)
    S = sum(w for w, _ in WP)
    A = 0
    i = 0
    while A < S and i < N:
        A += sum(WP[i])
        i += 1
    print(N-i)
