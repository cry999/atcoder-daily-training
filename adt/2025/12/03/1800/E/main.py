h1, h2, h3, w1, w2, w3 = map(int, input().split())

cnt = 0
for a11 in range(1, 31):
    for a12 in range(1, 31):
        a13 = h1-a11-a12
        if a13 < 1:
            # a13 は小さくなり続けるだけなのでこれ以上試す価値なし
            break
        if 30 < a13:
            # a12 が大きくなれば a13 が小さくなって条件を満たす
            # 可能性があるので continue
            continue
        # print('a11, a12, a13', a11, a12, a13)

        for a21 in range(1, 31):
            a31 = w1-a11-a21
            if a31 < 1:
                break
            if 30 < a31:
                continue

            for a22 in range(1, 31):
                a23 = h2-a21-a22
                # print('a21, a22, a23', a21, a22, a23)
                a32 = w2-a12-a22
                a33 = h3-a31-a32
                # print('a31, a32, a33', a31, a32, a33)
                if a32 < 1 or a23 < 1:
                    break
                if 30 < a32 or 30 < a23:
                    continue
                if a33 != w3-a13-a23:
                    continue
                if a33 < 1 or 30 < a33:
                    continue

                cnt += 1
print(cnt)
