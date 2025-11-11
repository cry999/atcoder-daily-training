Q = int(input())

queue = []
cur = 0
for _ in range(Q):
    query, *params = map(int, input().split())
    # print(f'query: {query}, params: {params}, queue: {queue}, cur: {cur}')
    if query == 1:
        c, x = params
        if len(queue) > 0 and queue[-1][0] == x:
            queue[-1] = (x, queue[-1][1]+c)
        else:
            queue.append((x, c))
    else:  # query == 2
        k = params[0]
        s = 0
        while k:
            x, c = queue[cur]
            # print(f'  processing: x={x}, c={c}, k={k}, s={s}')
            s += x * min(c, k)
            if c >= k:
                # print(f'    taking {k} of {c}')
                c, k = c-k, 0
                queue[cur] = (x, c)
            else:
                # print(f'    taking all {c} of {c}')
                c, k = 0, k-c
                queue[cur] = (x, c)
                cur += 1
        print(s)
