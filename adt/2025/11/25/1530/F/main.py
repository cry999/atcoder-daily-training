import bisect


N, Q = map(int, input().split())
*A, = map(int, input().split())
A.sort()

max_a = A[-1]
sum_a = [0]*(N+1)
for i in range(N):
    sum_a[i+1] = sum_a[i] + A[i]

for _ in range(Q):
    b = int(input())
    if b > max_a:
        print(-1)
        continue
    # # O(NQ):TLE
    # ans = sum(min(b-1, a) for a in A) + 1
    # print(ans)

    i = bisect.bisect_left(A, b-1)
    ans = sum_a[i] + (N-i)*(b-1) + 1
    print(ans)
