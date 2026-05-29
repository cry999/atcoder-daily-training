N, Q = map(int, input().split())
queries = [input().split() for _ in range(Q)]

while queries and queries[-1][0] != "3":
    queries.pop()

pc = 0
server_copy = True
ans = []
while queries:
    q, *args = queries.pop()
    # print(f"=== {q=} {args=} ===")
    # print(f"  {pc=} {server_copy=}")

    if q == "1":
        p = int(args[0])
        if p != pc:
            continue
        server_copy = True
    elif q == "2":
        p = int(args[0])
        s = args[1]
        if p != pc or server_copy:
            continue
        ans.append(s)
    else:  # q == '3'
        p = int(args[0])
        if not server_copy:
            continue
        server_copy = False
        pc = p

print("".join(reversed(ans)))
