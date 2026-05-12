from itertools import permutations

A, B = map(int, input().split())

ans = 0
for y in range(1, 201):
    for x in [-y, y]:
        for p, q, r in permutations([A, B, x]):
            if q - p == r - q:
                ans += 1
                break

print(ans)
