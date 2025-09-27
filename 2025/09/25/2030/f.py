HA, WA = map(int, input().split())
A = [input() for _ in range(HA)]

HB, WB = map(int, input().split())
B = [input() for _ in range(HB)]

HX, WX = map(int, input().split())
X = [input() for _ in range(HX)]


def index(s: str, sub: str) -> int:
    for (i, c) in enumerate(s):
        if c == sub:
            return i
    else:
        return len(s)


def compact(s: list[str], h: int, w: int) -> (list[str], int, int):
    max_l, min_r = w, 0
    max_u, min_d = h, 0

    for i in range(h):
        if any(c == '#' for c in s[i]):
            max_u = min(max_u, i)
            min_d = max(min_d, i)
        max_l = min(index(s[i], '#'), max_l)
        min_r = max(w - index(s[i][::-1], '#') - 1, min_r)

    new_h = min_d - max_u + 1
    new_w = min_r - max_l + 1
    new_s = [s[i][max_l:min_r+1] for i in range(max_u, min_d+1)]
    return new_s, new_h, new_w


A, HA, WA = compact(A, HA, WA)
B, HB, WB = compact(B, HB, WB)
X, HX, WX = compact(X, HX, WX)


def c_color(i: int, j: int, ia: int, ja: int, ib: int, jb: int) -> str:
    if 0 <= i-ia < HA and 0 <= j-ja < WA and A[i-ia][j-ja] == '#':
        return '#'
    if 0 <= i-ib < HB and 0 <= j-jb < WB and B[i-ib][j-jb] == '#':
        return '#'
    return '.'


def is_ok(ia: int, ja: int, ib: int, jb: int) -> bool:
    for i in range(HX):
        for j in range(WX):
            c = c_color(i, j, ia, ja, ib, jb)
            if c != X[i][j]:
                return False
    return True


for ia in range(HX-HA+1):
    for ja in range(WX-WA+1):
        # Aの左上をXの(ia, ja)に合わせる
        for ib in range(HX-HB+1):
            for jb in range(WX-WB+1):
                # Bの左上をXの(ib, jb)に合わせる
                if is_ok(ia, ja, ib, jb):
                    print('Yes')
                    exit()
print('No')
