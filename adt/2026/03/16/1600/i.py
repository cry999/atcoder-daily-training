N, M = map(int, input().split())
(*A,) = map(int, input().split())


class BIT:
    def __init__(self, n: int):
        self.n = n
        self.data = [0] * (self.n + 1)

    def add(self, i: int, x: int):
        while i <= self.n:
            self.data[i] += x
            i += i & -i

    def sum(self, i: int) -> int:
        s = 0
        while i > 0:
            s += self.data[i]
            i -= i & -i
        return s


# I[k] := A[i] = k となる i のリスト
I = [[] for _ in range(M)]

bit = BIT(M)
inv = 0
for i, a in enumerate(A):
    I[a].append(i)

    v = (a) % M
    inv += i - bit.sum(v + 1)
    bit.add(v + 1, 1)

print(inv)
for k in range(1, M):
    for j, i in enumerate(I[M - k]):
        # A[i] = M-k より右にある数字の個数
        inv -= N - i - 1
        # A[i] = M-k より右にある M-k の個数
        inv += len(I[M - k]) - j - 1
        # A[i] = M-k より左にある数字の個数
        inv += i
        # A[i] = M-k より左にある M-k の個数
        inv -= j
    print(inv)
