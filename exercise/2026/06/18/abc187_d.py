N = int(input())
towns = []

aoki_score = 0

for _ in range(N):
    a, b = map(int, input().split())
    aoki_score += a
    towns.append(a * 2 + b)

towns.sort(reverse=True)
takahashi_virtual_score = 0

ans = 0
for score in towns:
    takahashi_virtual_score += score
    ans += 1

    if takahashi_virtual_score > aoki_score:
        break
print(ans)
