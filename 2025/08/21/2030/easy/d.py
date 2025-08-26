available = [False] * 1001

for a in range(1, 143):
    for b in range(1, 143):
        i = 4*a*b + 3*a + 3*b
        if i > 1000:
            break
        available[i] = True

N = int(input())
S = list(map(int, input().split()))

count = 0
for s in S:
    if not available[s]:
        count += 1
print(count)
