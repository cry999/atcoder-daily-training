import heapq

N, K, X = map(int, input().split())
(*A,) = sorted(map(int, input().split()), reverse=True)

S = K * A[0]
cookies = tuple(0 if i != 0 else K for i in range(N))
queue = [(-S, cookies)]
x = 0

pushed = {cookies}
seen = set()


while queue and x < X:
    S, cookies = heapq.heappop(queue)
    if cookies in seen:
        continue
    seen.add(cookies)

    print(-S)
    x += 1
    for i in range(N - 1):
        if cookies[i] == 0:
            continue
        new_cookies = tuple(
            c - 1 if j == i else (c + 1 if j == i + 1 else c)
            for j, c in enumerate(cookies)
        )
        if new_cookies in seen or new_cookies in pushed:
            continue
        heapq.heappush(queue, (-(-S - A[i] + A[i + 1]), new_cookies))
        pushed.add(new_cookies)
