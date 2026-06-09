from sortedcontainers import SortedList

N, K = map(int, input().split())
(*P,) = map(int, input().split())

decks = []
removal_time = [-1] * N
front = SortedList()

for i in range(N):
    j = front.bisect_left((P[i], -1))
    if j == len(front):
        k = len(decks)
        decks.append([])
    else:
        _, k = front.pop(j)

    front.add((P[i], k))
    decks[k].append(P[i] - 1)
    if len(decks[k]) == K:
        # print(f"[DEBUG] {front=}, ({P[i]=}, {k=})")
        front.remove((P[i], k))
        for x in decks[k]:
            removal_time[x] = i + 1
# print(f"[DEBUG] {decks=}")
# print(f"[DEBUG] {removal_time=}")
for t in removal_time:
    print(t)
