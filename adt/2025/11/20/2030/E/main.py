# 全探索
N, M = map(int, input().split())
edges = [tuple(map(int, input().split())) for _ in range(M)]

min_deletion = M
# ノードの色分けを全探索
for bit in range(1 << N):
    # 右端から n bit 目が 1 なら黒(=True), そうでないなら白(=False)
    colors = [(bit >> i) & 1 == 1 for i in range(N)]
    # 全ての辺の両端が別の色かを確認。
    # 同じ色を繋ぐ辺の個数を最小化する。
    same = sum(colors[u-1] == colors[v-1] for u, v in edges)
    min_deletion = min(min_deletion, same)

print(min_deletion)
