N = int(input())
S = input()

ans = 0
for s in [S, S[::-1]]:
    i = 0
    while i < N:
        if s[i] != "-":
            i += 1
            continue

        i += 1
        lvl = 0
        while i < N and s[i] == "o":
            i += 1
            lvl += 1

        ans = max(ans, lvl)


print(ans if ans > 0 else -1)
