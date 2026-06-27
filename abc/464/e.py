H, W, Q = map(int, input().split())
S = [["A"] * W for _ in range(H)]
# cursors[c] := c 列の何行まで塗ったかを保持する。
cursors = [0] * W

# クエリは確定する順である逆順に処理する。
queries = []
for _ in range(Q):
    r, c, x = input().split()
    queries.append((int(r), int(c), x))
queries.reverse()

for r, c, x in queries:
    lo, hi = -1, W
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if cursors[mid] < r:
            hi = mid
        else:
            lo = mid
    # print(f"[DEBUG] {r=} {c=} {x=} {lo=} {hi=}")
    # print(f"[DEBUG] {cursors=}")
    for cc in range(hi, c):
        if cursors[cc] >= r:
            continue
        for rr in range(cursors[cc], r):
            S[rr][cc] = x
        cursors[cc] = r

print("\n".join("".join(s) for s in S))
