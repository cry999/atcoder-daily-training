H, W = map(int, input().split())
A = [[int(c) for c in input().split()] for _ in range(H)]

for i1 in range(H):
    for j1 in range(W):
        for i2 in range(i1, H):
            for j2 in range(j1, W):
                left = A[i1][j1] + A[i2][j2]
                right = A[i1][j2] + A[i2][j1]
                if left > right:
                    print('No')
                    exit()
print('Yes')
