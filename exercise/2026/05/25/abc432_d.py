N, X, Y = map(int, input().split())
areas = [(0, 0, Y - 1, X - 1)]

for _ in range(N):
    c, raw_a, raw_b = input().split()
    A, B = int(raw_a), int(raw_b)

    temp = []
    if c == "X":
        for i in range(len(areas)):
            d, l, u, r = areas[i]
            if r < A:
                # area が全て a より左にある場合は全体が b だけ下に移動する。
                areas[i] = (d - B, l, u - B, r)
            elif A <= l:
                # area が全て a より右にある場合は全体が b だけ上に移動する。
                areas[i] = (d + B, l, u + B, r)
            else:
                # area が a と交わる場合は、分割する。
                areas[i] = (d - B, l, u - B, A - 1)
                temp.append((d + B, A, u + B, r))
    else:  # c == 'Y':
        for i in range(len(areas)):
            d, l, u, r = areas[i]
            if d >= A:
                # area が全て a より上にある場合は全体が b だけ左に移動する。
                areas[i] = (d, l + B, u, r + B)
            elif u < A:
                # area が全て a より下にある場合は全体が b だけ右に移動する。
                areas[i] = (d, l - B, u, r - B)
            else:
                # area が a と交わる場合は、分割する。
                areas[i] = (d, l - B, A - 1, r - B)
                temp.append((A, l + B, u, r + B))
    areas.extend(temp)


class UnionFind:
    def __init__(self, n: int):
        self.n = n
        self.root = list(range(n))
        self.size = [1] * n

    def find(self, x: int):
        if self.root[x] == x:
            return x
        self.root[x] = self.find(self.root[x])
        return self.root[x]

    def union(self, x: int, y: int):
        x_root = self.find(x)
        y_root = self.find(y)
        if x_root == y_root:
            return False

        if self.size[x_root] < self.size[y_root]:
            x_root, y_root = y_root, x_root
        self.root[y_root] = x_root
        self.size[x_root] += self.size[y_root]
        return True


uf = UnionFind(len(areas))
for i, (d0, l0, u0, r0) in enumerate(areas):
    for j, (d1, l1, u1, r1) in enumerate(areas[i + 1 :]):
        j += i + 1
        if l1 - 1 <= r0 <= r1 + 1 or (r1 + 1 < r0 and l0 <= r1 + 1):
            if (r0 + 1 == l1 or l0 - 1 == r1) and (u0 + 1 == d1 or d0 - 1 == u1):
                continue
            elif d1 - 1 <= u0 <= u1 + 1:
                uf.union(i, j)
            elif u1 + 1 < u0 and d0 <= u1 + 1:
                uf.union(i, j)
            else:
                continue

n = 0
ans = [0] * len(areas)
for i in range(len(areas)):
    if uf.find(i) == i:
        n += 1
    d, l, u, r = areas[i]
    s = (u - d + 1) * (r - l + 1)
    ans[uf.find(i)] += s
print(n)
print(*sorted(filter(lambda x: x > 0, ans)))
