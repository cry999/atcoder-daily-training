A, B, K = map(int, input().split())

# f[na][nb] := na 個の a と nb 個の b を並べてできる文字列の数
# f[na][nb] = f[na-1][nb] + f[na][nb-1]
f = [[0] * (B + 1) for _ in range(A + 1)]

# 前計算する。
for na in range(1, A + 1):
    f[na][0] = 1
for nb in range(1, B + 1):
    f[0][nb] = 1

for na in range(1, A + 1):
    for nb in range(1, B + 1):
        f[na][nb] = f[na - 1][nb] + f[na][nb - 1]

# 先頭から a か b かを選んでいく。
# K が [1, f[A-1][B]] に含まれる時は先頭は a で、
# A を 1 減らして次の文字を考える。
# K が [f[A-1][B] + 1, f[A][B]] に含まれる場合は先頭は b で、
# B を 1 減らして、K を f[A-1][B] 減らして次の文字を考える。
ans = []
while A > 0 and B > 0:
    if K <= f[A - 1][B]:
        ans.append("a")
        A -= 1
    else:
        ans.append("b")
        K -= f[A - 1][B]
        B -= 1

ans.append("a" * A)
ans.append("b" * B)

print("".join(ans))
