from itertools import permutations

c = [0] * 9
for i in range(3):
    c[3 * i : 3 * i + 3] = map(int, input().split())


all_cnt = 0
target_cnt = 0
for p in permutations(range(9)):
    all_cnt += 1

    h = [[] for _ in range(3)]
    v = [[] for _ in range(3)]
    lu_rd = []  # (0, 0) (1, 1) (2, 2)
    ru_ld = []  # (0, 2) (1, 1) (2, 0)

    for x in p:
        i, j = divmod(x, 3)
        if len(h[i]) < 2:
            h[i].append(c[x])
        elif h[i][0] == h[i][1] and h[i][0] != c[x]:
            target_cnt += 1
            break
        if len(v[j]) < 2:
            v[j].append(c[x])
        elif v[j][0] == v[j][1] and v[j][0] != c[x]:
            target_cnt += 1
            break
        if i == j:
            if len(lu_rd) < 2:
                lu_rd.append(c[x])
            elif lu_rd[0] == lu_rd[1] and lu_rd[0] != c[x]:
                target_cnt += 1
                break
        if i + j == 2:
            if len(ru_ld) < 2:
                ru_ld.append(c[x])
            elif ru_ld[0] == ru_ld[1] and ru_ld[0] != c[x]:
                target_cnt += 1
                break

print(f"{(all_cnt - target_cnt) / all_cnt:.10f}")
