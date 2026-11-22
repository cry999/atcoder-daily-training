import sys
from collections import defaultdict

N = int(input())
S = input()

i0 = -1
count: defaultdict[str, int] = defaultdict(int)
for i in range(N):
    count[S[i]] += 1
    if all(count[c] > 0 for c in "ABC"):
        i0 = i
        break
if i0 == -1:
    print(0)
    sys.exit()

count = defaultdict(int)
j0 = -1
for j in range(N - 1, -1, -1):
    count[S[j]] += 1
    if all(count[c] > 0 for c in "ABC"):
        j0 = j
        break

# print(i0, j0)
i, j = i0 + 1, i0 + 1
count = defaultdict(int)
ans = 0
while i < j0:
    j = max(j, i)
    while any(count[c] == 0 for c in "ABC") and j < j0:
        count[S[j]] += 1
        j += 1
    if any(count[c] == 0 for c in "ABC"):
        break
    # print(i, j)
    ans += j0 - j + 1

    count[S[i]] -= 1
    i += 1
print(ans)
