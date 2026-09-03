from collections import Counter

N = int(input())
(*A,) = map(int, input().split())
c = Counter(A)
ans = sum(i * (n % 2) for i, n in c.items())
print(ans)
