from collections import deque


N, M = map(int, input().split())
S = list(input())
T = list(input())

queue = deque()

for i in range(N - M + 1):
    if S[i : i + M] == T:
        queue.append(i)


done = [False] * N
DONE = ["#"] * M
while queue:
    i = queue.popleft()
    if S[i : i + M] == DONE:
        continue
    if done[i]:
        continue
    S[i : i + M] = DONE[:]
    done[i] = True

    for j in range(max(0, i - M + 1), i + M):
        if N - j < M:
            break
        if done[j]:
            continue
        for k in range(M):
            if not (S[j + k] == "#" or S[j + k] == T[k]):
                break
        else:
            if S[j : j + M] != DONE:
                queue.append(j)

print("Yes" if all("#" == c for c in S) else "No")
