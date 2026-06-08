N = int(input())
mapping = {}

for i in range(N):
    a, b = input().split()
    mapping[a] = (b, i)

visited = [False] * N
for before, (after, i) in mapping.items():
    if visited[i]:
        continue

    visited[i] = True
    cur = after
    is_ok = True
    while True:
        if cur not in mapping:
            break

        a, i = mapping[cur]
        if visited[i]:
            is_ok = cur != before
            break

        visited[i] = True
        cur = a

    if not is_ok:
        print("No")
        break
else:
    print("Yes")
