n = int(input())
(*a,) = map(int, input().split())
q = int(input())
(*m,) = map(int, input().split())

available = [False] * (40_000 + 1)
for bit in range(1 << n):
    available[sum(a[i] for i in range(n) if bit & (1 << i))] = True

for mm in m:
    print("yes" if available[mm] else "no")
