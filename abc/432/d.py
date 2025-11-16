N, X, Y = map(int, input().split())
parts = [((0, X-1), (0, Y-1))]

for _ in range(N):
    C, A, B = input().split()
    A, B = int(A), int(B)
    if C == 'X':
        for i in range(len(parts)):
            (min_x, max_x), (min_y, max_y) = parts[i]
            if max_x < A:
                parts[i] = ((min_x, max_x), (min_y-B, max_y-B))
            elif A <= min_x:
                parts[i] = ((min_x, max_x), (min_y+B, max_y+B))
            else:
                parts[i] = ((min_x, A-1), (min_y-B, max_y-B))
                parts.append(((A, max_x), (min_y+B, max_y+B)))
    else:
        for i in range(len(parts)):
            (min_x, max_x), (min_y, max_y) = parts[i]
            if max_y < A:
                parts[i] = ((min_x-B, max_x-B), (min_y, max_y))
            elif A <= min_y:
                parts[i] = ((min_x+B, max_x+B), (min_y, max_y))
            else:
                parts[i] = ((min_x-B, max_x-B), (min_y, A-1))
                parts.append(((min_x+B, max_x+B), (A, max_y)))


class UnionFind:
    def __init__(self, n: int):
        self.parent = [i for i in range(n)]
        self.size = [1] * n
        self.data = [0] * n
        self.roots_set = set(range(n))

    def union(self, x: int, y: int):
        rx, ry = self.root(x), self.root(y)
        if rx == ry:
            return
        if self.size[rx] > self.size[ry]:
            rx, ry = ry, rx

        self.parent[ry] = rx
        self.size[rx] += self.size[ry]
        self.data[rx] += self.data[ry]
        self.roots_set.remove(ry)

    def root(self, x: int) -> int:
        if self.parent[x] == x:
            return x
        self.parent[x] = self.root(self.parent[x])
        return self.parent[x]

    def roots(self) -> list[int]:
        return list(self.roots_set)


uf = UnionFind(len(parts))

parts.sort()
for i in range(len(parts)):
    (min_x, max_x), (min_y, max_y) = parts[i]
    uf.data[i] = (max_x-min_x+1) * (max_y-min_y+1)

print(parts)
for i, u in enumerate(parts):
    (min_x1, max_x1), (min_y1, max_y1) = u
    for j, v in enumerate(parts[i+1:]):
        (min_x2, max_x2), (min_y2, max_y2) = v
        if max_x1+1 < min_x2 or max_x2+1 < min_x1:
            continue
        if max_y1+1 < min_y2 or max_y2+1 < min_y1:
            continue
        if max_x1+1 == min_x2 and not (max_y1+1 < min_y2 or max_y2+1 < min_y1):
            continue
        if max_x2+1 == min_x1 and not (max_y1+1 < min_y2 or max_y2+1 < min_y1):
            continue
        uf.union(i, i+1+j)

for r in uf.roots():
    print(uf.data[r])
