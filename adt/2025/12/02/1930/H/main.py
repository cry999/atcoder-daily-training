Q = int(input())

pages = {}


class Node:
    val: int = 0
    prev: 'Node' = None


class Page:
    head: Node = None
    tail: Node = None


cursor_head: Node = None
cursor_tail: Node = None
ans = []
for _ in range(Q):
    *query, = input().split()
    if query[0] == 'ADD':
        next = Node()
        next.val = int(query[1])
        next.prev = cursor_tail
        cursor_tail = next
        if not cursor_head:
            cursor_head = next
    elif query[0] == 'DELETE':
        if cursor_tail:
            cursor_tail = cursor_tail.prev
    elif query[0] == 'SAVE':
        page = Page()
        page.head = cursor_head
        page.tail = cursor_tail
        pages[int(query[1])] = page
    else:  # LOAD
        page = pages.get(int(query[1]), Page())
        cursor_head = page.head
        cursor_tail = page.tail

    ans.append(cursor_tail.val if cursor_tail else -1)

print(*ans)
