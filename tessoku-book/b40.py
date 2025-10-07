N = int(input())
A = list(map(int, input().split()))

cnt = {}

for a in A:
    cnt[a % 100] = cnt.get(a % 100, 0) + 1

ans = 0
for i in range(1, 50):
    ans += cnt.get(i, 0) * cnt.get(100-i, 0)

ans += cnt.get(0, 0) * (cnt.get(0, 0) - 1) // 2
ans += cnt.get(50, 0) * (cnt.get(50, 0) - 1) // 2

print(ans)
