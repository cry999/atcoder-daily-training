from sys import stdin, setrecursionlimit

input = stdin.readline
setrecursionlimit(10**7)

T = int(input())

DIRS = {
    "L": [0, -1],
    "R": [0, +1],
    "U": [-1, 0],
    "D": [+1, 0],
}

for _ in range(T):
    N, A, B = map(int, input().split())

    if N % 2:
        print("No")
        continue

    if (A + B) % 2 == 0:
        print("No")
        continue

    s1 = []
    while A - 2 * len(s1) > 2:
        s1.append("R" * (N - 1) + "D" + "L" * (N - 1) + "D")

    s2 = []
    while B - 2 * len(s2) > 2:
        s2.append("DRUR")

    if B % 2:
        s2.append("RD")
    else:
        s2.append("DR")

    s3 = []
    while N - B - 2 * len(s3) >= 2:
        s3.append("RURD")

    s4 = []
    while N - A - 2 * len(s4) >= 2:
        s4.append("D" + "L" * (N - 1) + "D" + "R" * (N - 1))

    print("Yes")
    print("".join(s1), end="")
    # print("s1", "".join(s1))
    print("".join(s2), end="")
    # print("s2", "".join(s2))
    print("".join(s3), end="")
    # print("s3", "".join(s3))
    print("".join(s4), end="")
    # print("s4", "".join(s4))
    print()
