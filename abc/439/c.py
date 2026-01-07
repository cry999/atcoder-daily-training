N = int(input())

counts = [0] * (N + 1)
for x in range(1, N + 1):
    if (x**2) * 2 > N:
        break
    for y in range(x + 1, N + 1):
        s = x**2 + y**2
        if s > N:
            break
        counts[s] += 1

ans = []
for n, c in enumerate(counts):
    if c == 1:
        ans.append(n)
print(len(ans))
print(*ans)
