N, M = map(int, input().split())
(*C,) = map(int, input().split())
dishes = {}
for _ in range(N):
    a, b = map(int, input().split())
    dishes[a] = dishes.get(a, 0) + b

ans = 0
for i, c in enumerate(C):
    i += 1
    if i not in dishes:
        continue

    use = min(c, dishes[i])
    ans += use

print(ans)
