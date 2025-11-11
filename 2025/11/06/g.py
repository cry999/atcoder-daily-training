N, M = map(int, input().split())
X = list(set(map(int, input().split())))
X.sort()

# dist[i]: X[i+1] - X[i]: 0 から i 番目の位置と i+1 番目の家の距離
dist = [X[i+1]-X[i] for i in range(len(X)-1)]
dist.sort(reverse=True)

print(sum(dist[M-1:]))
