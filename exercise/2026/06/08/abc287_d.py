S = input()
T = input()

N = len(S)
M = len(T)

# prefix[x] := S の先頭から x 文字と T の先頭から x 文字が一致しているか？
prefix = [False] * (M + 1)
# suffix[x] := S の末尾から x 文字と T の末尾から x 文字が一致しているか？
suffix = [False] * (M + 1)

prefix[0] = True
for i in range(M):
    ok = S[i] == T[i] or S[i] == "?" or T[i] == "?"
    prefix[i + 1] = prefix[i] and ok

suffix[0] = True
for i in range(M):
    ok = S[N - 1 - i] == T[M - 1 - i] or S[N - 1 - i] == "?" or T[M - 1 - i] == "?"
    suffix[i + 1] = suffix[i] and ok

for x in range(M + 1):
    if prefix[x] and suffix[M - x]:
        print("Yes")
    else:
        print("No")
