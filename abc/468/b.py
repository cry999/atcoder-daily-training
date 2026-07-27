M, D = map(int, input().split())
S = input()

is_guard = [False] * M

for i in range(M):
    if S[i] == "G":
        for x in range(D + 1):
            if i - x >= 0:
                is_guard[i - x] = True
            if i + x < M:
                is_guard[i + x] = True

ans = sum(not g for g in is_guard)
print(ans)
