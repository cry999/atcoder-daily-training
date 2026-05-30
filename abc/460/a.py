N, M = map(int, input().split())

num = 0
while M > 0:
    M = N % M
    num += 1

print(num)
