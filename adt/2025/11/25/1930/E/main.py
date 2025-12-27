from collections import defaultdict


N = int(input())
counts = defaultdict(int)

for _ in range(N):
    S = input()
    if counts[S] == 0:
        print(S)
    else:
        print(f'{S}({counts[S]})')
    counts[S] += 1
