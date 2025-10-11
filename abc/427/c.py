N, M = map(int, input().split())
edges = [tuple(map(int, input().split())) for _ in range(M)]

ans = min(sum(
    # 頂点 u と v が同じ色なら削除が必要
    ((mask >> (u-1)) & 1) == ((mask >> (v-1)) & 1) for u, v in edges
)  # 頂点の色分けを全探索（ビット列で表現、0 or 1）
    for mask in range(1 << N)
)

print(ans)
