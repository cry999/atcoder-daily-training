from sys import stdin, stdout

input = stdin.readline


def print(*args):
    stdout.write(" ".join(map(str, args)))
    stdout.write("\n")


def main():
    H, W, N = map(int, input().split())

    chocolates: list[int] = []
    for i in range(N):
        h, w = map(int, input().split())
        chocolates.append((h, w, i))

    pos = [None] * N

    chocolates_sorted_by_h = sorted(chocolates, key=lambda x: x[0])
    chocolates_sorted_by_w = sorted(chocolates, key=lambda x: x[1])

    used = [False] * N

    hi, wi = 1, 1
    x, y = 1, 1
    for _ in range(N):
        while used[chocolates_sorted_by_h[-hi][2]]:
            hi += 1

        if chocolates_sorted_by_h[-hi][0] == H:
            h, w, idx = chocolates_sorted_by_h[-hi]
            used[idx] = True
            hi += 1
            W -= w
            pos[idx] = (x, y)
            y += w
            continue

        while used[chocolates_sorted_by_w[-wi][2]]:
            wi += 1

        h, w, idx = chocolates_sorted_by_w[-wi]
        used[idx] = True
        wi += 1
        H -= h
        pos[idx] = (x, y)
        x += h

    for h, w in pos:
        print(h, w)


main()
