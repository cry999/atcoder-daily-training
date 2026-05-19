N, Q = map(int, input().split())


class E:
    def __init__(self, n: int, prev: "E" = None, next: "E" = None):
        self.n = n
        self.prev = prev
        if prev is not None:
            prev.next = self
        self.next = next
        if next is not None:
            next.prev = self


decks = [E(i) for i in range(N)]
cards = [E(i, prev=decks[i]) for i in range(N)]

for _ in range(Q):
    C, P = map(int, input().split())

    card = cards[C - 1]
    p = card.prev
    if p is not None:
        p.next = None
    pile = cards[P - 1]
    card.prev = pile
    pile.next = card

ans = []
for i in range(N):
    head = decks[i]

    a = 0
    while head is not None:
        head = head.next
        a += 1

    ans.append(a - 1)

print(*ans)
