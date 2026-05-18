S = input()

ans = 0
for i, s in enumerate(S):
    if s != "C":
        continue

    n = min(i, len(S) - i - 1)
    ans += n + 1

print(ans)
