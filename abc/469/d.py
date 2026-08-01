N, M = map(int, input().split())
pairs = [tuple(map(int, input().split())) for _ in range(M)]

x, y = pairs[0]
# x か y のどちらかは答えに必ず含まれる。

ans = set()

for fixed in [x, y]:
    # 相方候補
    others = set(range(1, N + 1))
    for a, b in pairs:
        if a == fixed or b == fixed:
            continue

        others &= {a, b}
        if not others:
            # fixed を固定しても全てをおおえない。
            break

    ans |= {(min(fixed, o), max(fixed, o)) for o in others if o != fixed}
print(len(ans))
