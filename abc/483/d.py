N = int(input())
(*A,) = map(int, input().split())

max1 = max2 = 0
min1 = min2 = 0

ans = 0
for a in A:
    max2 = max(0, max2 + a, max1 - a)
    min2 = min(0, min2 + a, min1 - a)

    max1 = max(0, max1 + a)
    min1 = min(0, min1 + a)

    ans = max(ans, max2, -min2)
print(ans + 1)
