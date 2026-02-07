from collections import deque

Q = int(input())

# snakes[i] := (i 番目に並んでいる蛇の先頭の位置, そいつ自身の長さ)
snakes = deque()
total_length = 0
removed_length = 0
for _ in range(Q):
    query, *args = map(int, input().split())
    if query == 1:
        l = args[0]
        snakes.append((total_length, l))
        total_length += l
    elif query == 2:
        _, l = snakes.popleft()
        removed_length += l
    else:
        k = args[0]
        head, _ = snakes[k - 1]
        print(head - removed_length)
