import sys

input = sys.stdin.readline
print = sys.stdout.write


N, M = map(int, input().split())
g = [[] for _ in range(N)]
black = bytearray(N)


for _ in range(M):
    x, y = map(int, input().split())
    g[y - 1].append(x - 1)

Q = int(input())
ans = []
stack = []
for i in range(Q):
    q, v = map(int, input().split())
    v -= 1
    if q == 1:
        if black[v]:
            continue

        stack.append(v)
        black[v] = 1
        while stack:
            u = stack.pop()
            for w in g[u]:
                if black[w]:
                    continue
                black[w] = 1
                stack.append(w)
    else:  # q == 2
        ans.append("Yes\n" if black[v] else "No\n")

print("".join(ans))
