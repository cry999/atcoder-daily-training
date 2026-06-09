from heapq import heappop as pop, heappush as push


N, M, X = map(int, input().split())

delays = [-1] * M
delays[0] = X

# graph[a] := (b, s, t, i)
# a: 出発地点
# b: 到着地点
# s: 出発時刻
# t: 到着時刻
# i: 辺番号
graph = [[] for _ in range(N + 1)]

queue = []

for i in range(M):
    # a を時刻 s に出発して b に時刻 t に到着する
    a, b, s, t = map(int, input().split())
    graph[a].append((b, s, t, i))
    if i == 0:
        push(queue, ())
