class UnionFind:
    def __init__(self, n):
        self.root = list(range(n))
        self.size = [1] * n

    def find(self, x):
        if self.root[x] != x:
            self.root[x] = self.find(self.root[x])
        return self.root[x]

    def merge(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False

        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx
        self.size[rx] += self.size[ry]
        self.root[ry] = rx
        return True

    def groups(self):
        group_dict = {}
        for i in range(len(self.root)):
            group_dict.setdefault(self.find(i), []).append(i)

        return list(group_dict.values())


MAX = 2 * 10**5
MOD = 998244353

frac = [1] * (MAX + 1)
for i in range(2, MAX + 1):
    frac[i] = (frac[i - 1] * i) % MOD

invf = [1] * (MAX + 1)
for i in range(2, MAX + 1):
    q, r = divmod(MOD, i)
    invf[i] = (-invf[r] * q) % MOD
for i in range(2, MAX + 1):
    invf[i] = (invf[i] * invf[i - 1]) % MOD

N, M = map(int, input().split())
S = input()

u = UnionFind(N)
for _ in range(M):
    a, b = map(int, input().split())
    u.merge(a - 1, b - 1)

ans = 1
for g in u.groups():
    ans = (ans * frac[len(g)]) % MOD
    print(f"[DEBUG] {g=}")

    counter = [0] * 26
    for i in g:
        counter[ord(S[i]) - ord("a")] += 1

    for c in counter:
        ans = (ans * invf[c]) % MOD

print(ans)
