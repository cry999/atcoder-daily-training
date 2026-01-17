h1, h2, h3, w1, w2, w3 = map(int, input().split())

ans = 0
for a11 in range(1, min(h1, w1) + 1):
    for a12 in range(1, h1 - a11):
        a13 = h1 - a11 - a12
        if a13 < 1:
            break

        for a21 in range(1, min(w1 - a11, h2 + 1)):
            a31 = w1 - a11 - a21
            if a31 < 1:
                break

            for a22 in range(1, min(h2 - a21, w2 - a12)):
                a23 = h2 - a21 - a22
                a32 = w2 - a12 - a22
                a33 = h3 - a31 - a32
                if a23 < 1 or a32 < 1 or a33 < 1:
                    continue
                if a13 + a23 + a33 == w3:
                    ans += 1

print(ans)
