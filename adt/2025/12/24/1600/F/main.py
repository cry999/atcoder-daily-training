N = int(input())
(*P,) = map(int, input().split())

# 後ろから見ていって、> になる初めての場所を探す。
# > の左側を右側の中で一つ小さい値と交換して
# 右側は単調減少にソートすれば良い。

for i in range(N - 1, 0, -1):
    if P[i - 1] < P[i]:
        continue

    # P[i-1] より小さい数の中で最大のものを探す。
    j = i
    while j + 1 < N and P[j + 1] < P[i - 1]:
        j += 1

    # P[i-1] と P[j] を交換する。
    P[i - 1], P[j] = P[j], P[i - 1]
    # > の右側を単調減少にソートする。
    P[i:] = sorted(P[i:], reverse=True)
    break

print(*P)
