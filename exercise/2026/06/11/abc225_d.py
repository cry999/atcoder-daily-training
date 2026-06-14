class Node:
    next: "Node"
    prev: "Node"
    v: int

    def __init__(self, v: int):
        self.v = v
        self.next = None
        self.prev = None


N, Q = map(int, input().split())
trains = [Node(i) for i in range(N + 1)]

for _ in range(Q):
    q, *args = map(int, input().split())
    if q == 1:
        x, y = args
        tx, ty = trains[x], trains[y]
        tx.next = ty
        ty.prev = tx
    elif q == 2:
        x, y = args
        tx, ty = trains[x], trains[y]
        tx.next = None
        ty.prev = None
    else:
        x = args[0]
        head = trains[x]
        while head.prev is not None:
            head = head.prev

        cur = head
        num = 0
        ans = []
        while cur is not None:
            num += 1
            ans.append(cur.v)
            cur = cur.next

        print(num, *ans)
