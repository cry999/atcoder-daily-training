N = int(input())
RC = [tuple(map(int, input().split())) for _ in range(N)]
max_r = max(RC, key=lambda x: x[0])[0]
min_r = min(RC, key=lambda x: x[0])[0]
max_c = max(RC, key=lambda x: x[1])[1]
min_c = min(RC, key=lambda x: x[1])[1]

r = (max_r + min_r) // 2 + ((max_r + min_r) % 2)
c = (max_c + min_c) // 2 + ((max_c + min_c) % 2)

ans = max(
    max_r - r, r - min_r,
    max_c - c, c - min_c,
)

print(ans)
