(*S,) = map(int, list(input()))


def solve(S: list[int]):
    hist = [0] * 10
    for c in S:
        hist[c] += 1

    a = [
        [1, 6],
        [2, 4],
        [3, 2],
        [4, 8],
        [5, 6],
        [6, 4],
        [7, 2],
        [8, 8],
        [9, 6],
    ]

    b = [
        [1, 2],
        [2, 8],
        [3, 6],
        [4, 4],
        [5, 2],
        [6, 8],
        [7, 6],
        [8, 4],
        [9, 2],
    ]

    if len(S) == 1 and S[0] == 8:
        return True

    def check_a(x: int, y: int):
        hist[x] -= 1
        hist[y] -= 1
        s = sum(hist[i] for i in range(0, 10, 2))
        ok = hist[x] >= 0 and hist[y] >= 0 and (s > 0 or len(S) == 2)
        hist[x] += 1
        hist[y] += 1
        return ok

    def check_b(x: int, y: int):
        hist[x] -= 1
        hist[y] -= 1
        s = sum(hist[i] for i in range(1, 10, 2))
        ok = hist[x] >= 0 and hist[y] >= 0 and s > 0
        hist[x] += 1
        hist[y] += 1
        return ok

    for x, y in a:
        if check_a(x, y):
            return True

    for x, y in b:
        if check_b(x, y):
            return True

    return False


if solve(S):
    print("Yes")
else:
    print("No")
