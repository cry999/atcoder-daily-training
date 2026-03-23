S = input()

i = 0
cnt = 0
while i < len(S):
    if S[i] == "0" and i + 1 < len(S) and S[i + 1] == "0":
        i += 1
    i += 1
    cnt += 1

print(cnt)
