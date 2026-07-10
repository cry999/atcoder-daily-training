H, W = map(int, input().split())
K = int(input())

HW = (H + 1) * (W + 1)
jungle = [0] * HW
ocean = [0] * HW
ice = [0] * HW

for h in range(H):
    s = input()
    for w in range(W):
        p = (h + 1) * (W + 1) + (w + 1)
        if s[w] == "J":
            jungle[p] = 1
        elif s[w] == "O":
            ocean[p] = 1
        else:  # s[w] == 'I'
            ice[p] = 1

for h in range(H + 1):
    for w in range(W):
        p = h * (W + 1) + w
        n = p + 1
        jungle[n] += jungle[p]
        ocean[n] += ocean[p]
        ice[n] += ice[p]
for h in range(H):
    for w in range(W + 1):
        p = h * (W + 1) + w
        n = p + W + 1
        jungle[n] += jungle[p]
        ocean[n] += ocean[p]
        ice[n] += ice[p]


for _ in range(K):
    a, b, c, d = map(int, input().split())
    p0 = c * (W + 1) + d
    p1 = c * (W + 1) + b - 1
    p2 = (a - 1) * (W + 1) + d
    p3 = (a - 1) * (W + 1) + b - 1
    j = jungle[p0] - jungle[p1] - jungle[p2] + jungle[p3]
    o = ocean[p0] - ocean[p1] - ocean[p2] + ocean[p3]
    i = ice[p0] - ice[p1] - ice[p2] + ice[p3]
    print(j, o, i)
