S = [""] + [input() for _ in range(3)]
T = input()

print("".join(S[int(c)] for c in T))
