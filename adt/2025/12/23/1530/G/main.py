N, R, C = map(int, input().split())
S = input()


def dir(s: str) -> tuple[int, int]:
    if s == "N":
        return (-1, 0)
    if s == "S":
        return (1, 0)
    if s == "W":
        return (0, -1)
    if s == "E":
        return (0, 1)


def rev(d: tuple[int, int]) -> tuple[int, int]:
    return (-d[0], -d[1])


takahashi = (R, C)

smoke = (0, 0)
smokes = set()
smokes.add(smoke)

ans = ""
for s in S:
    dr, dc = rev(dir(s))

    smoke = (smoke[0] + dr, smoke[1] + dc)
    smokes.add(smoke)

    takahashi = (takahashi[0] + dr, takahashi[1] + dc)
    if takahashi in smokes:
        ans += "1"
    else:
        ans += "0"
print(ans)
