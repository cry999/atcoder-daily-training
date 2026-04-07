N = int(input())
S = [input() for _ in range(N)]
S.reverse()
T = []

max_s_len = max(len(s) for s in S)

for i in range(max_s_len):
    T.append("".join(s[i] if i < len(s) else "*" for s in S).rstrip("*"))

print("\n".join(T))
