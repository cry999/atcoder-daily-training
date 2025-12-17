from collections import defaultdict


N, Q = map(int, input().split())

friends = defaultdict(set)

for _ in range(Q):
    T, A, B = map(int, input().split())

    if T == 1:
        friends[A].add(B)
    elif T == 2:
        friends[A].discard(B)
    else:
        if A in friends[B] and B in friends[A]:
            print('Yes')
        else:
            print('No')
