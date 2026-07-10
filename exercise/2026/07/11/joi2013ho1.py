N = int(input())
(*A,) = map(int, input().split())

line = [[A[0], 0]]

for a in A:
    if line[-1][0] == a:
        line.append([a, 1])
    else:
        line[-1][0] = a
        line[-1][1] += 1

line.append([-1, 0])

M = len(line)
ans = 0
for i in range(1, M - 1):
    score = line[i][1]
    score += line[i - 1][1]
    score += line[i + 1][1]
    ans = max(ans, score)
print(ans)
