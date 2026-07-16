N, K = map(int, input().split())

score = 0
diff = []

for _ in range(N):
    a, b = map(int, input().split())
    score += a
    diff.append(b - a)

# print(f"[DEBUG] {score=}, {diff=}")

for k in range(K):
    cur_s = 0
    cur_l = 0

    max_s = 0
    max_l = 0
    max_r = 0

    for i in range(N):
        cur_s += diff[i]

        if cur_s > max_s:
            max_s = cur_s
            max_l = cur_l
            max_r = i + 1

        if cur_s < 0:
            cur_s = 0
            cur_l = i + 1

    if max_s <= 0:
        break

    score += max_s
    # print(f"[DEBUG] [{k=}] {max_s=} {max_l=} {max_r=}")

    for i in range(max_l, max_r):
        diff[i] = -diff[i]

print(score)
