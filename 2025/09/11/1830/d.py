import bisect

N, M = map(int, input().split())
UV = sorted(
    [tuple(map(int, input().split())) for _ in range(M)],
)


def search(t: tuple) -> bool:
    i = bisect.bisect_left(UV, t)
    return i < len(UV) and UV[i] == t


# print(UV)
count = 0
for (a, b) in UV:
    for c in range(b+1, N+1):
        if search((a, c)) and search((b, c)):
            count += 1
            # print(a, b, c)
print(count)
