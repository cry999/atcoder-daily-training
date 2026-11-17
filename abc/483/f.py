from collections import defaultdict

N = int(input())
AB = [tuple(map(int, input().split())) for _ in range(N)]

Q = int(input())
X = [int(input()) for _ in range(Q)]
MAX_X = max(X)

counter: defaultdict[tuple[int, int], int] = defaultdict(int)
offset = 0

for a, b in AB:
    offset += a % b
    counter[b, (-a) % b] += 1

d = [N] * (MAX_X + 1)
for (b, r), c in counter.items():
    for x in range(r or b, MAX_X + 1, b):
        d[x] -= b * c

ans = [0] * (MAX_X + 1)
ans[0] = offset

for x in range(1, MAX_X + 1):
    ans[x] = ans[x - 1] + d[x]

print(*[ans[x] for x in X], sep="\n")
