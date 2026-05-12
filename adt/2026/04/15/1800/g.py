N, K = map(int, input().split())

if K == 1:
    ans = []
    for i in range(N):
        print("?", i + 1)
        ans.append(int(input()))
    print("!", *ans)
    exit()

ans = []
s = 0
for i in range(K):
    print("?", *[j + 1 for j in range(K + 1) if j != i])
    T = int(input())
    ans.append(T)
    s += T

a = [-1] * N
a[K] = s % 2

print("?", *[j + 1 for j in range(K)])
T = int(input())

for i in range(K):
    a[i] = (T + a[K] - ans[i]) % 2

for i in range(K + 1, N):
    print("?", *[j + 1 for j in range(K - 1)], i + 1)
    T = int(input())
    a[i] = (T - ans[K - 1] + a[K]) % 2

print("!", *a)
