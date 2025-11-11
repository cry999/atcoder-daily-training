# TODO: 解けてない
N, M, K = map(int, input().split())
g = [[] for _ in range(N+1)]

for _ in range(M):
    a, b = map(int, input().split())
    # 両方向で登録すると、重複が面倒なので、
    # 後ろで計算しやすいように、ページ番号の小さい方から
    # 大きい方への繋がりだけを保存する
    a, b = min(a, b), max(a, b)
    g[a].append(b)

max_conns = 0
MAX_PAGE = N-K+1
for start_section in range(K):
    # i ページ目から始まる N-K+1 ページの章に入る
    # 最大の繋がりの数を求める
    conns = 0
    end_section = start_section+MAX_PAGE
    for diff in range(MAX_PAGE):
        page = start_section+diff+1
        for to_page in g[page]:
            conns += to_page <= end_section
    max_conns = max(max_conns, conns)
print(max_conns)
