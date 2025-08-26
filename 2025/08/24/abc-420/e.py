N, Q = map(int, input().split())

black_nums = [0] * (N+1)
is_black = [False] * (N+1)
groups = [i for i in range(N+1)]

for _ in range(Q):
    query = list(map(int, input().split()))
    print('query:', query)

    if query[0] == 1:
        u, v = query[1], query[2]
        groups[u] = groups[v] = min(groups[u], groups[v])
    elif query[0] == 2:
        pass
    else:  # 3
        pass

    print('black_nums:', black_nums)
    print('is_black:', is_black)
    print('groups:', groups)
