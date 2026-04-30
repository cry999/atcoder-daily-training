from atcoder.segtree import SegTree

N = int(input())
S = list(input())
Q = int(input())


def idx(c: str) -> int:
    return ord(c) - ord("a")


hist = [0] * 26
segtree = [SegTree(lambda x, y: x + y, 0, [0] * N) for _ in range(26)]

for i, c in enumerate(S):
    hist[idx(c)] += 1
    segtree[idx(c)].set(i, 1)


for _ in range(Q):
    q, *args = input().split()

    if q == "1":
        raw_x, c = args
        x = int(raw_x) - 1
        hist[idx(S[x])] -= 1
        segtree[idx(S[x])].set(x, 0)
        S[x] = c
        hist[idx(S[x])] += 1
        segtree[idx(S[x])].set(x, 1)
    else:  # q == '2'
        l, r = map(lambda x: int(x) - 1, args)

        offset = 0
        cnt = [segtree[c].prod(l, r + 1) for c in range(26)]
        for c in range(26):
            if (c < idx(S[l]) or idx(S[r]) < c) and cnt[c] > 0:
                print("No")
                break

            if idx(S[l]) < c < idx(S[r]) and cnt[c] != hist[c]:
                print("No")
                break

            la = l + offset
            ra = la + cnt[c] - 1
            if segtree[c].prod(la, ra + 1) != cnt[c]:
                print("No")
                break

            offset += cnt[c]
        else:
            print("Yes")
