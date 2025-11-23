N = int(input())
*A, = map(int, input().split())

for i, a in enumerate(A):
    ans = -1
    for j in range(i):
        b = A[j]
        if b > a:
            ans = j+1
    print(ans)
