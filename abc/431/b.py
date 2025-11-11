X = int(input())
N = int(input())

*W, = map(int, input().split())
Q = int(input())

equips = {}
weight = X
for _ in range(Q):
    P = int(input())
    if equips.get(P, False):
        weight -= W[P-1]
        equips[P] = False
    else:
        weight += W[P-1]
        equips[P] = True
    print(weight)
