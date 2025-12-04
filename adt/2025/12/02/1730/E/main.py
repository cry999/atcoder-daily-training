N, M = map(int, input().split())
A = [None for _ in range(M)]

for i in range(M):
    _ = int(input())
    *A[i], = set(map(int, input().split()))

cnt = 0
for b in range(1 << M):
    for x in range(1, N+1):
        for i, a in enumerate(A):
            if not (b >> i) & 1:
                continue
            if x in a:
                break
        else:
            break
    else:
        cnt += 1

print(cnt)
