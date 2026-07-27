from itertools import permutations

N = int(input())
P = tuple(map(int, input().split()))
Q = tuple(map(int, input().split()))

if Q <= P:
    print(0)
else:
    ans = 0
    for x in permutations(range(1, N + 1)):
        if P < x < Q:
            ans += 1
    print(ans)
