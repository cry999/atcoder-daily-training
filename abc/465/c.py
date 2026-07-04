N = int(input())
S = input()


class Node:
    def __init__(self, v: int):
        self.v = v
        self.next: "Node" = None
        self.prev: "Node" = None


head = Node(1)
tail = head
rev = False
for i in range(1, N):
    node = Node(i + 1)
    if S[i - 1] == "x":
        if not rev:
            tail.next = node
            node.prev = tail
            tail = node
        else:
            tail.prev = node
            node.next = tail
            tail = node
    else:
        if not rev:
            head.prev = node
            node.next = head
            head = node
        else:
            head.next = node
            node.prev = head
            head = node

        head, tail = tail, head
        rev = not rev

ans = []
while head is not None:
    ans.append(head.v)
    if rev:
        head = head.prev
    else:
        head = head.next
if S[-1] == "o":
    ans.reverse()
print(*ans)
