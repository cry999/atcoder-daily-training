import sys

input = sys.stdin.readline

N = int(input())
tasks = []
for _ in range(N):
    cost, deadline = map(int, input().split())
    tasks.append((deadline, cost))

t = 0
for deadline, cost in sorted(tasks):
    if t + cost > deadline:
        print("No")
        break
    t += cost
else:
    print("Yes")
