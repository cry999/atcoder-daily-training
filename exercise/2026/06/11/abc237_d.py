N = int(input())
S = input()


class Node:
    def __init__(self, value: int):
        self.next: "Node" = None
        self.prev: "Node" = None
        self.value = value

    def insert_left(self, new: "Node"):
        new.next = self
        new.prev = self.prev

        if self.prev is not None:
            self.prev.next = new

        self.prev = new
        return new

    def insert_right(self, new: "Node"):
        new.prev = self
        new.next = self.next

        if self.next is not None:
            self.next.prev = new

        self.next = new
        return new


cur = Node(0)

for i, s in enumerate(S):
    n = Node(i + 1)
    if s == "L":
        cur = cur.insert_left(n)
    else:
        cur = cur.insert_right(n)

head = cur
while head.prev:
    head = head.prev

ans = []
while head:
    ans.append(head.value)
    head = head.next

print(*ans)
