import math

N = int(input())


def icbrt(n: float):
    # 3乗根の初期推測値を計算
    approx = int(n ** (1 / 3))
    # 実際の3乗が元の数 n と一致するかチェック
    if (approx + 1) ** 3 <= n:
        approx += 1
    elif approx**3 > n:
        approx -= 1
    return approx


M = icbrt(4 * N / 3)
for d in range(1, M + 1):
    if N % d != 0:
        continue

    # 判別式 12*N/d - 3*d^2 は [1, M] の範囲では正だけど念の為チェック
    if 12 * N // d - 3 * d**2 < 0:
        continue

    a = math.isqrt(12 * N // d - 3 * d**2)
    if a**2 != 12 * N // d - 3 * d**2:
        # 判別式が平方数でない場合は整数解なし
        continue

    b = -3 * d + a
    if b % 6 != 0:
        # b が 6 の倍数でない場合は整数解なし
        continue

    y = b // 6
    x = y + d
    if y <= 0:
        continue

    print(x, y)

    break
else:
    print(-1)
