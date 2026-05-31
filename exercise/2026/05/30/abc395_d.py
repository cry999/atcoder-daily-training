N, Q = map(int, input().split())

# クエリで指定される巣の番号と内部管理用の巣の index の対応表
# norm: クエリ用 -> 内部用
norm = [i for i in range(N + 1)]
# rev: 内部用 -> クエリ用
rev = [i for i in range(N + 1)]

# 鳩の入っている巣の番号。この番号は内部管理用を指す。
birds = [i for i in range(N + 1)]

for _ in range(Q):
    q, *args = map(int, input().split())

    if q == 1:
        # 鳩 a を巣 b に移動させる
        a, b = args
        birds[a] = norm[b]
    elif q == 2:
        # 巣 a と巣 b を入れ替える。
        # 鳩を一羽ずつ入れ替えるのは計算量が足りないので、クエリ用の名前を変更するだけ
        a, b = args
        norm[a], norm[b] = norm[b], norm[a]
        rev[norm[a]], rev[norm[b]] = rev[norm[b]], rev[norm[a]]
        # rev 更新はただの swap なので norm を入れ替えた後でも問題ない。
    else:
        a = args[0]
        print(rev[birds[a]])
