N = int(input())
S = input()
(*C,) = map(int, input().split())

# left[i][j] := i 文字目までを 0 と 1 が連続しない文字列にした上で、
# 末尾 (i 文字目) を j にするための操作回数
left = [[0] * 2 for _ in range(N)]
for j in range(2):
    left[0][j] = 0 if S[0] == str(j) else C[0]

for i in range(1, N):
    for j in range(2):
        left[i][j] = left[i - 1][1 - j] + (0 if S[i] == str(j) else C[i])

# right[i][j] := i 文字目から先を 0 と 1 が連続しない文字列にした上で、
# 末尾 (i 文字目) を j にするための操作回数
right = [[0] * 2 for _ in range(N)]
for j in range(2):
    right[-1][j] = 0 if S[-1] == str(j) else C[-1]

for i in range(N - 2, -1, -1):
    for j in range(2):
        right[i][j] = right[i + 1][1 - j] + (0 if S[i] == str(j) else C[i])

ans = float("inf")
for i in range(N - 1):
    for j in range(2):
        ans = min(ans, left[i][j] + right[i + 1][j])

print(ans)
# print(left)
# print(right)
