from collections import Counter

N, K = map(int, input().split())
(*A,) = map(int, input().split())
counter = Counter(A)

max_count = max(counter.values())

ans = 0
for k in range(1, K + 1):
    if max_count - 1 <= counter[k] <= max_count:
        ans += 1
print(ans)
