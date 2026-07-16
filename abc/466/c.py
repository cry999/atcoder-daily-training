N = int(input())

r = 0
ans = 0
for l in range(N - 1):
    r = max(r, l + 1)
    while r < N:
        print(f"? {l+1} {r+1}")
        if input() == "Yes":
            r += 1
        else:
            break
    n = r - l - 1
    ans += n
print("!", ans)
