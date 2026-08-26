N, Q = map(int, input().split())
vertices = []

for _ in range(N):
    x, y = map(int, input().split())
    vertices.append((x, y))

pre_x = [0] * (2 * N)
pre_y = [0] * (2 * N)
pre_c = [0] * (2 * N)

for i in range(2 * N - 1):
    x1, y1 = vertices[i % N]
    x2, y2 = vertices[(i + 1) % N]
    c = x1 * y2 - x2 * y1

    pre_c[i + 1] = pre_c[i] + c
    pre_x[i + 1] = pre_x[i] + (x1 + x2) * c
    pre_y[i + 1] = pre_y[i] + (y1 + y2) * c

for _ in range(Q):
    l, r = map(int, input().split())
    l, r = l - 1, r - 1

    if r < l:
        r += N

    sum_c = pre_c[r] - pre_c[l]
    sum_x = pre_x[r] - pre_x[l]
    sum_y = pre_y[r] - pre_y[l]

    # l -> l+1 -> ... -> r-1 -> r を計算して
    # 最後に r -> l を計算する必要がある
    x1, y1 = vertices[r % N]
    x2, y2 = vertices[l % N]

    c = x1 * y2 - x2 * y1

    sum_c += c
    sum_x += (x1 + x2) * c
    sum_y += (y1 + y2) * c

    gx, gy = sum_x / (3 * sum_c), sum_y / (3 * sum_c)

    # print(f"[DEBUG] {r=}, {l=}, {n=}: {sum_x=}, {sum_y=}")
    print(gx, gy)
