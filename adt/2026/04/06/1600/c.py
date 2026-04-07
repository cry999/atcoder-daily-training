N, M = map(int, input().split())
products = []
for _ in range(N):
    p, c, *f = map(int, input().split())
    products.append((p, c, set(f)))
products.sort(key=lambda x: (-x[0], x[1]))

for i in range(N):
    pi, ci, fi = products[i]
    for j in range(i + 1, N):
        # print(f"test: {i=}, {j=}")
        pj, cj, fj = products[j]

        if not fi.issubset(fj):
            # print(f"  {fi=} is not subset of {fj=}")
            continue
        if not (pi > pj or cj > ci):
            # print(f"  {pi=} > {pj=} and {cj=} == {ci=}")
            continue

        print("Yes")
        break
    else:
        continue
    break
else:
    print("No")
