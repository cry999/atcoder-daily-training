N = int(input())

T = []
A = []

for _ in range(N):
    t, _, *a = map(int, input().split())
    T.append(t)
    A.append(a)

acquired = [False]*N
queue = [N-1]
total_time = 0

while queue:
    skill = queue.pop()
    if acquired[skill]:
        continue
    acquired[skill] = True
    total_time += T[skill]

    for prereq in A[skill]:
        prereq -= 1
        if acquired[prereq]:
            continue
        queue.append(prereq)

print(total_time)
