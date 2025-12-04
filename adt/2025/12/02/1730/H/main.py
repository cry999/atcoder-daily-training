from atcoder.segtree import SegTree


N, Q = map(int, input().split())
S = input()
st = SegTree(
    lambda x, y: x+y, 0,
    [int(S[i] == S[i+1]) for i in range(N-1)] + [0],
)

for _ in range(Q):
    q, l, r = map(int, input().split())
    l, r = l-1, r-1
    if q == 1:
        if l > 0:
            st.set(l-1, 1-st.prod(l-1, l))
        if r <= N-1:
            st.set(r, 1-st.prod(r, r+1))
    else:
        print('Yes' if st.prod(l, r) == 0 else 'No')
