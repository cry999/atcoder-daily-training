N, M = map(int, input().split())
features: list[tuple[int, set[int]]] = []

for _ in range(N):
    p, c, *f = map(int, input().split())
    features.append((p, set(f)))

features.sort(key=lambda x: x[1])
features.sort(key=lambda x: x[0], reverse=True)

for i in range(N):
    pi, fi = features[i]
    for j in range(i + 1, N):
        pj, fj = features[j]
        if pi == pj and fj > fi:
            print("Yes")
            break
        if pi > pj and fj >= fi:
            print("Yes")
            break
    else:
        continue
    break
else:
    print("No")
