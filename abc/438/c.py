N = int(input())
*A, = map(int, input().split())

q = []
for i in range(N):
    if len(q) >= 3 and A[q[-3]] == A[q[-2]] == A[q[-1]] == A[i]:
        q.pop()
        q.pop()
        q.pop()
    else:
        q.append(i)

print(len(q))
