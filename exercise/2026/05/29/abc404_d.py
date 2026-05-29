N, M = map(int, input().split())
(*C,) = map(int, input().split())

# zoo[i] := 動物園iにいる動物のリスト
zoo = [0] * N
for animal in range(M):
    _, *A = map(lambda x: int(x) - 1, input().split())
    for zoo_idx in A:
        zoo[zoo_idx] |= 1 << animal

ans = 2 * sum(C)
for bit in range(1 << (2 * N)):
    price = 0
    exists_1 = 0
    exists_2 = 0

    for i in range(2 * N):
        if (bit >> i) & 1 == 0:
            continue
        i %= N
        price += C[i]
        exists_2 |= zoo[i] ^ ((exists_1 ^ zoo[i]) & zoo[i])
        exists_1 |= (exists_1 ^ zoo[i]) & zoo[i]

    if exists_1 == exists_2 == (1 << M) - 1:
        ans = min(ans, price)

print(ans)
