from itertools import combinations

n, k = map(int, input().split())
(*a,) = map(int, input().split())

ans = 10**18
for selected in combinations(range(1, n), k - 1):
    selected = set(selected)

    tallest = a[0]
    cost = 0
    for i in range(1, n):
        if i in selected:
            if a[i] <= tallest:
                cost += tallest - a[i] + 1
                tallest += 1
            else:
                tallest = a[i]
        else:
            tallest = max(tallest, a[i])
    ans = min(ans, cost)
print(ans)
