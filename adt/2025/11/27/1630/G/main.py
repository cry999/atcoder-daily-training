class Node:
    left: 'Node'
    right: 'Node'
    value: int

    def __init__(self, value: int):
        self.right = self.left = None
        self.value = value

    def __str__(self) -> str:
        s = []
        c = self
        while c:
            s.append(str(c.value))
            c = c.right
        return ' '.join(s)

    def __repr__(self) -> str:
        return self.__str__()


head = Node(0)
cur = head

N = int(input())
S = input()

for i in range(N):
    s = S[i]
    node = Node(i+1)
    if s == 'L':
        # cur.left <here> cur cur.right
        node.left = cur.left
        if cur.left:
            cur.left.right = node
        node.right = cur
        cur.left = node
        if not node.left:
            head = node
    elif s == 'R':
        # cur.left cur <here> cur.right
        node.right = cur.right
        if cur.right:
            cur.right.left = node
        node.left = cur
        cur.right = node
    cur = node

ans = []
cur = head
while cur:
    ans.append(cur.value)
    cur = cur.right
print(*ans)
