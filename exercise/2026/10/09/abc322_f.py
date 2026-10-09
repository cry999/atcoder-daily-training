# >>> atcoder-stat >>>
# started_at  = 2026-10-09T12:55:31+09:00
# solved_at   = 2026-10-09T14:19:03+09:00
# duration_ms = 5012237
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


class SegTree:
    def __init__(self, s):
        n = len(s)
        self.log = (n - 1).bit_length()
        self.size = size = 1 << self.log

        self.m0 = [0] * (2 * size)
        self.m1 = [0] * (2 * size)
        self.pre = [0] * (2 * size)
        self.suf = [0] * (2 * size)
        self.lazy = bytearray(size)

        for i, c in enumerate(s, size):
            if c == "1":
                self.m1[i] = 1
                self.pre[i] = self.suf[i] = 1
            else:
                self.m0[i] = 1
                self.pre[i] = self.suf[i] = -1

        for k in range(size - 1, 0, -1):
            self.pull(k)

    def pull(self, k):
        a = k << 1
        b = a | 1
        m0, m1 = self.m0, self.m1
        pre, suf = self.pre, self.suf

        # 葉は左詰めなので、空区間は右側にだけ現れる
        if pre[b] == 0:
            m0[k], m1[k] = m0[a], m1[a]
            pre[k], suf[k] = pre[a], suf[a]
            return

        x0, y0 = m0[a], m0[b]
        x1, y1 = m1[a], m1[b]

        z0 = x0 if x0 > y0 else y0
        z1 = x1 if x1 > y1 else y1

        p, q = pre[a], suf[b]
        x, y = suf[a], pre[b]

        if x > 0 and y > 0:
            joined = x + y
            if joined > z1:
                z1 = joined
            if x0 == 0:
                p += y
            if y0 == 0:
                q += x

        elif x < 0 and y < 0:
            joined = -x - y
            if joined > z0:
                z0 = joined
            if x1 == 0:
                p += y
            if y1 == 0:
                q += x

        m0[k], m1[k] = z0, z1
        pre[k], suf[k] = p, q

    def flip_node(self, k):
        self.m0[k], self.m1[k] = self.m1[k], self.m0[k]
        self.pre[k] = -self.pre[k]
        self.suf[k] = -self.suf[k]

        if k < self.size:
            self.lazy[k] ^= 1

    def push(self, k):
        if self.lazy[k]:
            self.flip_node(k << 1)
            self.flip_node(k << 1 | 1)
            self.lazy[k] = 0

    def push_path(self, l, r):
        for h in range(self.log, 0, -1):
            if (l >> h) << h != l:
                self.push(l >> h)
            if (r >> h) << h != r:
                self.push((r - 1) >> h)

    def flip(self, l, r):
        l += self.size
        r += self.size
        self.push_path(l, r)

        l0, r0 = l, r
        while l < r:
            if l & 1:
                self.flip_node(l)
                l += 1
            if r & 1:
                r -= 1
                self.flip_node(r)
            l >>= 1
            r >>= 1

        for h in range(1, self.log + 1):
            if (l0 >> h) << h != l0:
                self.pull(l0 >> h)
            if (r0 >> h) << h != r0:
                self.pull((r0 - 1) >> h)

    def query(self, l, r):
        l += self.size
        r += self.size
        self.push_path(l, r)

        left, right = [], []
        while l < r:
            if l & 1:
                left.append(l)
                l += 1
            if r & 1:
                r -= 1
                right.append(r)
            l >>= 1
            r >>= 1

        # 区間を左から右の順に並べる
        left.extend(reversed(right))

        best = run = 0
        m0, m1 = self.m0, self.m1
        pre, suf = self.pre, self.suf

        for k in left:
            if m1[k] > best:
                best = m1[k]

            p = pre[k]
            if p > 0 and run + p > best:
                best = run + p

            if m0[k] == 0:
                # 区間全体が 1 なので、直前の連続に追加
                run += p
            else:
                tail = suf[k]
                run = tail if tail > 0 else 0

        return best


N, Q = map(int, input().split())
seg = SegTree(input().strip())

ans = []
for _ in range(Q):
    c, l, r = map(int, input().split())
    if c == 1:
        seg.flip(l - 1, r)
    else:
        ans.append(str(seg.query(l - 1, r)))

print("\n".join(ans))
