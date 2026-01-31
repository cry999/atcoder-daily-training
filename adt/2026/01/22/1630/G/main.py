from collections import defaultdict
from sortedcontainers import SortedDict

N = int(input())
K = [0] * N
A = [SortedDict(float) for _ in range(N)]

for i in range(N):
    k, *a = map(int, input().split())
    K[i] = k
    for v in a:
        A[i][v] = A[i].get(v, 0) + 1 / k

ans = 0
for i in range(N):
    for j in range(i + 1, N):
        ai, aj = A[i], A[j]
        used = set()

        same_number_prob = 0
        # for number, prob in ai.items():
        #     same_number_prob += prob * aj[number]
        #     used.add(number)
        #
        # for number, prob in aj.items():
        #     if number in used:
        #         continue
        #     same_number_prob += prob * ai[number]
        key_i, key_j = ai.keys(), aj.keys()
        ii, jj = 0, 0
        while ii < len(key_i) and jj < len(key_j):
            while ii < len(key_i) and key_i[ii] < key_j[jj]:
                ii += 1

            if ii >= len(key_i):
                break

            while jj < len(key_j) and key_i[ii] > key_j[jj]:
                jj += 1

            if jj >= len(key_j):
                break

            if ii < len(key_i) and jj < len(key_j) and key_i[ii] == key_j[jj]:
                key = key_i[ii]
                same_number_prob += ai[key] * aj[key]

                ii += 1
                jj += 1

        ans = max(ans, same_number_prob)

print(f"{ans:.15f}")
