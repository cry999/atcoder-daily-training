N = int(input())
S = input()

max_level = 0
level = 0
for i in range(N):
    if S[i] == 'o':
        level += 1
    else:
        max_level = max(max_level, level)
        level = 0

level = 0
for i in range(N - 1, -1, -1):
    if S[i] == 'o':
        level += 1
    else:
        max_level = max(max_level, level)
        level = 0

if max_level == 0:
    print(-1)
else:
    print(max_level)
