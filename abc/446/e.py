M, A, B = map(int, input().split())

ans = 0
ok_step = set()
ng_step = set()
for x in range(1, M):
    for y in range(1, M):
        s1, s2 = x, y
        visited = set()
        ok = True
        while True:
            if s2 == 0:
                ok = False
                break
            if (s1, s2) in ok_step:
                ok = True
                break
            if (s1, s2) in ng_step:
                ok = False
                break
            if (s1, s2) in visited:
                break

            visited.add((s1, s2))
            s1, s2 = s2, (s1 * B + s2 * A) % M

        if ok:
            ok_step |= visited
            ans += 1
        else:
            ng_step |= visited

print(ans)
