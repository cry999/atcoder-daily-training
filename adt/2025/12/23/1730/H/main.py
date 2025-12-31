L, N1, N2 = map(int, input().split())
compressed_x1 = [tuple(map(int, input().split())) for _ in range(N1)]
compressed_x2 = [tuple(map(int, input().split())) for _ in range(N2)]

for i in range(1, N1):
    compressed_x1[i] = (
        compressed_x1[i][0],
        compressed_x1[i][1] + compressed_x1[i - 1][1],
    )
for i in range(1, N2):
    compressed_x2[i] = (
        compressed_x2[i][0],
        compressed_x2[i][1] + compressed_x2[i - 1][1],
    )

i1, i2 = 0, 0
i = 0
ans = 0
while i1 < N1 and i2 < N2:
    v1, l1 = compressed_x1[i1]
    v2, l2 = compressed_x2[i2]

    if v1 == v2:
        ans += min(l1, l2) - i

    i = min(l1, l2)
    i1 += l1 == i
    i2 += l2 == i

print(ans)
