S = input()
pos = {ord(S[i]) - ord("A"): i for i in range(26)}

ans = sum(abs(pos[i] - pos[i + 1]) for i in range(25))
print(ans)
