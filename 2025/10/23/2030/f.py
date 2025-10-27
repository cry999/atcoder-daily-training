h1, h2, h3, w1, w2, w3 = map(int, input().split())
h1, h2, h3 = sorted([h1, h2, h3])
w1, w2, w3 = sorted([w1, w2, w3])

# print(h1, h2, h3, w1, w2, w3)

count = 0
for a11 in range(1, min(h1-1, w1-1)):
    for a12 in range(1, min(h1-a11, w2-1)):
        a13 = h1-a11-a12
        if a13 < 1 or w3-2 < a13:
            continue
        for a21 in range(1, min(h2-1, w1-a11)):
            for a22 in range(1, min(h2-a21, w2-a12)):
                a23 = h2-a21-a22
                if a23 < 1 or w3-a13-1 < a23:
                    continue
                a31 = w1-a11-a21
                a32 = w2-a12-a22
                a33 = w3-a13-a23
                if a31 < 1 or a32 < 1 or a33 < 1 or a31+a32+a33 != h3:
                    continue
                # print('------')
                # print(a11, a12, a13)
                # print(a21, a22, a23)
                # print(a31, a32, a33)
                count += 1
print(count)
