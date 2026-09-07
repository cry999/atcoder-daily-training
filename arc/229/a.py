X = int(input())

S = list(
    "ARARARARARARARARARARARARARARARARARARARARARARARARARCRCRCRCRCRCRCRCRCRCRCRCRCRCRCRCRCRCRCRCRCRCRCRC"
)
N = 600 - X

op = 0
while op < N:
    for i in range(len(S) - 2):
        if S[i : i + 3] == ["A", "R", "C"]:
            S[i], S[i + 2] = S[i + 2], S[i]
            op += 1
            if op == N:
                print("".join(S))
                exit()

print("".join(S))
