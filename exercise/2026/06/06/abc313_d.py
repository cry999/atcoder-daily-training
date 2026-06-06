N, K = map(int, input().split())

a = [0] * N

for k in range(1, K):
    print("?", *[x + 1 for x in range(K + 1) if x != k])

    T = int(input())
    a[0] = (a[0] + T) % 2
    a[k] = T

print("?", *[x + 1 for x in range(K)])
T = int(input())
a[0] = (a[0] + T) % 2


for k in range(K, N):
    print("?", *[x + 1 for x in range(1, K)], k + 1)
    a[k] = (int(input()) + a[0] + T) % 2

for k in range(1, K):
    a[k] = (a[k] + T + a[K]) % 2

print("!", *a)
