import sys

input = sys.stdin.readline


C = [[0] * 62 for _ in range(62)]
for i in range(62):
    C[i][0] = C[i][i] = 1
    for j in range(1, i):
        C[i][j] = C[i - 1][j - 1] + C[i - 1][j]
for _ in range(int(input())):
    l, r = map(int, input().split())
    r += 1
    d = [0] * 62
    while l < r:
        x = min(1 << ((r - l).bit_length() - 1), l & -l)
        c = x.bit_length() - 1
        p = l.bit_count()
        for i in range(c + 1):
            d[p + i] += C[c][i]
        for i in range(60, -1, -1):
            d[i] = max(d[i], d[i + 1])
        l += x
    print(d[0])
