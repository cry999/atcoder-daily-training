N = int(input())
*A, = map(int, input().split())

pos = [0] * N
for i, a in enumerate(A):
    pos[a-1] = i
# print(rev_a)
ans = []
for i in range(N):
    if A[i] == i+1:
        continue
    # print(A)
    j = pos[i]
    pos[A[j]-1] = i
    pos[A[i]-1] = j
    A[i], A[j] = A[j], A[i]
    ans.append((i+1, j+1))

print(len(ans))
for op in ans:
    print(*op)
