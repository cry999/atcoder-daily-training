from sortedcontainers import SortedList

N = int(input())
(*A,) = map(int, input().split())
M = 10**8

other = SortedList(A)
sum_a = sum(other)
n = N

ans = 0
for i in range(N - 1):
    a = A[i]
    sum_a -= a
    n -= 1
    other.remove(a)
    j = other.bisect_left(M - a)
    ans += a * n + sum_a - (n - j) * M
print(ans)
