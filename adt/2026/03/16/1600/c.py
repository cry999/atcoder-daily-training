N = int(input())

ans = ""
for _ in range(N):
    c, sl = input().split()
    l = int(sl)

    if len(ans) + l > 100:
        ans = "Too Long"
        break

    ans += c * l

print(ans)
