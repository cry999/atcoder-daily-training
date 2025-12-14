S = [input() for _ in range(9)]


def in_grid(p: tuple[int, int]) -> bool:
    return all(0 <= x < 9 for x in p)


def pone_exists(p: tuple[int, int]) -> bool:
    return S[p[0]][p[1]] == '#'


cnt = 0
for r in range(9):
    for c in range(9):
        for dr in range(1, 9):
            for dc in range(9):
                ps = [
                    (r, c),
                    (r+dr, c+dc),
                    (r+dr+dc, c+dc-dr),
                    (r+dc, c-dr),
                ]
                if any(not in_grid(p) for p in ps):
                    continue
                if all(pone_exists(p) for p in ps):
                    # print(ps)
                    cnt += 1
print(cnt)
