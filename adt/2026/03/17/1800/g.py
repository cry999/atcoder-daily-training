N, K = map(int, input().split())

qa = [0] * (K + 1)
s = 0
for i in range(K + 1):
    print("?", *[j + 1 for j in range(K + 1) if j != i])
    qa[i] = int(input())
    s ^= qa[i]

ans = [-1] * N
for i in range(K + 1):
    ans[i] = s ^ qa[i]

q = [i + 1 for i in range(K - 1)]
s = 0
for i in range(K - 1):
    s ^= ans[i]

for i in range(K + 1, N):
    q.append(i + 1)
    print("?", *q)
    a = int(input())
    ans[i] = s ^ a
    q.pop()

print("!", *ans)
