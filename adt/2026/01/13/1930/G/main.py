N = int(input())
S = input()

max_n = int("".join(sorted(S, reverse=True)))

ans = 0
for i in range(max_n + 1):
    if i * i > max_n:
        break
    n = i * i
    s = int("".join(sorted(f"{n:0{N}d}", reverse=True)))

    ans += s == max_n
print(ans)
