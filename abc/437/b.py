H, W, N = map(int, input().split())
A = [list(map(int, input().split())) for _ in range(H)]
B = [int(input()) for _ in range(N)]

print(max(
    sum(b in A[h] for b in B)
    for h in range(H)
))
