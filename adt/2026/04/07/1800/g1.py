N = int(input())
S = list(input())
Q = int(input())

# last_op[i] := i 番目の文字を最後に操作したクエリ。
last_op = [-1] * N

last_upper_lower_index = -1
last_upper_lower = ""

for q in range(Q):
    t, *args = input().split()
    if t == "1":
        x, c = int(args[0]) - 1, args[1]

        S[x] = c
        last_op[x] = q
    else:
        last_upper_lower = t
        last_upper_lower_index = q

for i in range(N):
    if last_upper_lower_index > last_op[i]:
        if last_upper_lower == "3":
            S[i] = S[i].upper()
        else:
            S[i] = S[i].lower()

print("".join(S))
