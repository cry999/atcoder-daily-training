N, M = map(int, input().split())

first: dict[int, int] = {}
second: dict[int, dict[int, int]] = {}
for _ in range(M):
    a, b = map(int, input().split())
    a -= 1
    b -= 1

    _ = first.setdefault(a, 0)
    first[a] += 1

    _ = second.setdefault(a, {})
    _ = second[a].setdefault(b, 0)
    second[a][b] += 1

max1_v, max2_v = 0, 0
max1_i, max2_i = -1, -1
for i in range(N):
    if first.get(i, 0) > max1_v:
        max2_v, max2_i = max1_v, max1_i
        max1_v, max1_i = first[i], i
    elif first.get(i, 0) > max2_v:
        max2_v, max2_i = first[i], i

for i in range(N):
    max_v, max_i = max1_v, max1_i
    if i == max1_i:
        max_v, max_i = max2_v, max2_i

    max3_v, max3_i = 0, -1
    for k, v in second.get(i, {}).items():
        if v + first.get(k, 0) > max3_v:
            max3_v, max3_i = v + first.get(k, 0), k
        if v + first.get(k, 0) == max3_v and k < max3_i:
            max3_v, max3_i = v + first.get(k, 0), k

    if max_v > max3_v:
        print(max_i + 1)
    elif max_v == max3_v:
        print(min(max_i, max3_i) + 1)
    else:
        print(max3_i + 1)
