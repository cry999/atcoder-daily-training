N = int(input())

for _ in range(N):
    (*A,) = map(int, input().split())
    ans = []
    for i, a in enumerate(A):
        if A:
            ans.append(i + 1)
    print(*ans)
