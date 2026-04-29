N = int(input())
(*A,) = map(int, input().split())

Q = int(input())

next_node = [-1] * (N + Q)
prev_node = [-1] * (N + Q)
rev = {}
val = [A[i] if i < N else -1 for i in range(N + Q)]

for i in range(N):
    a = A[i]
    if i + 1 < N:
        next_node[i] = i + 1
    else:
        next_node[i] = -2  # tail
    if i - 1 >= 0:
        prev_node[i] = i - 1
    rev[a] = i

for qi in range(Q):
    q, *args = map(int, input().split())

    if q == 1:
        # insert 'y' after 'x'
        x, y = args
        rev[y] = N + qi
        val[N + qi] = y

        nxt_i = next_node[rev[x]]

        next_node[rev[x]] = rev[y]
        prev_node[rev[y]] = rev[x]

        next_node[rev[y]] = nxt_i
        if nxt_i >= 0:
            prev_node[nxt_i] = rev[y]

    else:  # q == 2
        # remove 'x'
        x = args[0]

        prev_i = prev_node[rev[x]]
        next_i = next_node[rev[x]]

        if prev_i >= 0:
            next_node[prev_i] = next_i
        if next_i >= 0:
            prev_node[next_i] = prev_i

        prev_node[rev[x]] = next_node[rev[x]] = -1

head = -1
for i in range(N + Q):
    if prev_node[i] == -1 and next_node[i] != -1:
        head = i
        break

ans = []
while head != -2:
    ans.append(val[head])
    head = next_node[head]

print(*ans)
