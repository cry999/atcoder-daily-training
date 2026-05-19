S = input()
T = input()
N = len(S)

TI = [0] * len(T)

indexes = {}
for i, c in enumerate(S):
    indexes.setdefault(c, []).append(i)

ans = N * (N + 1) // 2
for t in T:
    if t not in indexes:
        print(ans)
        exit()

l = 0  # 禁止文字列を計算する最左端
while l < len(S):
    p = l - 1
    for ti, t in enumerate(T):
        while TI[ti] < len(indexes[t]) and indexes[t][TI[ti]] <= p:
            TI[ti] += 1
        if TI[ti] == len(indexes[t]):
            p = N
        else:
            p = indexes[t][TI[ti]]

    if TI[0] < len(indexes[T[0]]) and TI[-1] < len(indexes[T[-1]]):
        a = indexes[T[0]][TI[0]]  # 最小禁止文字列の最左端
        b = indexes[T[-1]][TI[-1]]  # 最小禁止文字列の最右端
        forbidden = max(0, a - l + 1) * max(N - b, 0)
        ans -= forbidden
        l = indexes[T[0]][TI[0]] + 1
        continue
    else:
        break

print(ans)
