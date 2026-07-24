N = int(input())

min_r = 10**18
ans = -min_r

for _ in range(N):
    r = int(input())
    ans = max(ans, r - min_r)
    min_r = min(min_r, r)
print(ans)
