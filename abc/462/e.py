T = int(input())

for _ in range(T):
    a, b, x, y = map(int, input().split())
    # x, y の正負は関係ない
    x, y = abs(x), abs(y)

    # 移動について、基本は右と上だけを使う。それ以外はどう考えてもコストが無駄。
    # ただし、上 -> 右 -> 下 で右への移動を実現するコスト (3A) が単純な右 (B)
    # より低コストになることはありうる。この場合は、A と 3B / B と 3A を交換する。

    if 3 * a < b:
        b = 3 * a
    elif 3 * b < a:
        a = 3 * b

    min_c, max_c = min(a, b), max(a, b)
    # 移動については、X -> Y / Y -> X と方向転換する瞬間に同じコストを利用できるので、
    # これを利用してトータルの低コストを実現する。
    # 方向転換の最大回数は 2*min(x, y)。

    n = 2 * min(x, y)
    q, r = divmod(max(x, y) - min(x, y), 2)

    # print(f"{n=}, {q=}, {r=}")
    if x > y:
        ans = min_c * n + a * (q + r) + b * q
    else:
        ans = min_c * n + b * (q + r) + a * q
    print(ans)
