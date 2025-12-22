rt, ct, ra, ca = map(int, input().split())
N, M, L = map(int, input().split())
S = []
for _ in range(M):
    s, a = input().split()
    S.append((s, int(a)))

T = []
for _ in range(L):
    t, b = input().split()
    T.append((t, int(b)))

for i in range(M-1):
    S[i+1] = (S[i+1][0], S[i+1][1]+S[i][1])
for i in range(L-1):
    T[i+1] = (T[i+1][0], T[i+1][1]+T[i][1])

# S, T からターンの範囲を求める。
# その間の移動をシミュレートする。
# O(N+M) で可能。

# 逆方向の組み合わせのリスト
revdirs = {'UD', 'DU', 'LR', 'RL'}


def move(dir: str, diff: int, pos: tuple[int, int]) -> tuple[int, int]:
    r, c = pos
    if dir == 'L':
        c -= diff
    elif dir == 'R':
        c += diff
    elif dir == 'U':
        r -= diff
    else:  # s == 'D'
        r += diff
    return r, c


time = 0
si, ti = 0, 0
ans = 0
while si < M and ti < L:
    s, a = S[si]
    t, b = T[ti]

    # 移動回数
    n = min(a, b) - time

    # コリジョン計算
    #
    # 同じ場所になるパターンは以下のいづれか
    # 上記の 3 パターン以外では衝突はあり得ない。
    if rt == ra and ct == ca:
        # 同じ位置にいて、同じ方向に進む場合
        if s == t:
            ans += n
    elif rt == ra:
        # R の値が等しいかつ以下のいづれか（横方向の衝突）
        #   a. (ct < ca で s == 'R' and t == 'L')
        #   b. (ct > ca で s == 'L' and t == 'R')
        # print(f'  {s+t=}, {ca-ct=}, {2*n=}')
        if ct < ca and s+t == 'RL' and ca-ct <= 2*n and (ca-ct) % 2 == 0:
            ans += 1
        # print(f'  {t+s=}, {ct-ca=}, {2*n=}')
        if ca < ct and t+s == 'RL' and ct-ca <= 2*n and (ct-ca) % 2 == 0:
            ans += 1
    elif ct == ca:
        # C の値が等しいかつ以下のいづれか（縦方向の衝突）
        #   a. (rt < ra で s == 'D' and t == 'U')
        #   b. (rt > ra で s == 'U' and t == 'D')
        if rt < ra and s+t == 'DU' and ra-rt <= 2*n and (ra-rt) % 2 == 0:
            ans += 1
        if ra < rt and t+s == 'DU' and rt-ra <= 2*n and (rt-ra) % 2 == 0:
            ans += 1
    else:
        # R, C 両方異なる場合、R と C の差が等しく、
        # 移動距離いないである必要があり、さらには方向性の制約
        # を満たす必要がある。
        if abs(rt-ra) == abs(ct-ca) and abs(rt-ra) <= n:
            if ca < ct and ra < rt and s+t in ('UR', 'LD'):
                ans += 1
            if ca < ct and ra > rt and s+t in ('DR', 'LU'):
                ans += 1
            if ca > ct and ra < rt and s+t in ('RD', 'UL'):
                ans += 1
            if ca > ct and ra > rt and s+t in ('RU', 'DL'):
                ans += 1

                # 移動する
    rt, ct = move(s, n, (rt, ct))
    ra, ca = move(t, n, (ra, ca))

    if a == b:
        si += 1
        ti += 1
    elif a < b:
        si += 1
    else:
        ti += 1
    time += n

print(ans)
