S = [input() for _ in range(5)]

ans = 5
for i in range(5):
    ans = min(ans, S[i].count("."))

for j in range(5):
    ans = min(ans, sum(S[i][j] == "." for i in range(5)))

ans = min(ans, sum(S[i][i] == "." for i in range(5)))
ans = min(ans, sum(S[i][4 - i] == "." for i in range(5)))

print(ans)
