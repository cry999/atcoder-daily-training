from atcoder.segtree import SegTree

N, M = map(int, input().split())
st = SegTree(min, M + 1, M + 1)

for _ in range(N):
    L, R = map(int, input().split())
    st.set(L, min(st.get(L), R))

ans = 0
for l in range(1, M + 1):
    r = st.prod(l, M + 1)
    # print(l, r, r - l)
    ans += r - l

print(ans)
