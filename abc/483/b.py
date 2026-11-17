from collections import deque

N, Q = map(int, input().split())
(*K,) = map(int, input().split())
deck = list(range(N, 0, -1))

for k in K:
    q: deque[int] = deque()
    for _ in range(k):
        # print(f"[DEBUG] {K=}")
        q.append(deck.pop())
    while q:
        deck.append(-q.popleft())
    # print(f"[DEBUG] {deck=}")

for k in deck[::-1]:
    print(k)
