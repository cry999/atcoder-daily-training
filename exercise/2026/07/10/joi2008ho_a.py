import sys

input = sys.stdin.readline

N = int(input())

line = []
for i in range(N):
    c = int(input())
    if i % 2 == 0:
        if line and line[-1][0] == c:
            line[-1][1] += 1
        else:
            line.append([c, 1])
    else:
        line[-1][0] = c
        line[-1][1] += 1
        while len(line) >= 2 and line[-2][0] == line[-1][0]:
            _, n = line.pop()
            line[-1][1] += n

print(sum(n for c, n in line if c == 0))
