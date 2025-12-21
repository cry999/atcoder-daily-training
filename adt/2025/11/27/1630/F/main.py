N = int(input())
*A, = map(int, input().split())

prev = {}

B = []
for i in range(N):
    a = A[i]
    if a in prev:
        B.append(prev[a])
    else:
        B.append(-1)
    prev[a] = i+1

print(*B)
