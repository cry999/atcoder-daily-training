h1, h2, h3, w1, w2, w3 = map(int, input().split())

ans = 0
for a11 in range(1, min(w1 - 2, h1 - 2) + 1):
    for a12 in range(1, min(w2 - 2, h1 - a11 - 1) + 1):
        a13 = h1 - a11 - a12
        for a21 in range(1, min(w1 - a11 - 1, h2 - 2) + 1):
            a31 = w1 - a11 - a21
            for a22 in range(1, min(w2 - a12 - 1, h2 - a21 - 1) + 1):
                a23 = h2 - a21 - a22
                a32 = w2 - a12 - a22

                # check a33
                if h3 - a31 - a32 == w3 - a13 - a23 > 0:
                    ans += 1
print(ans)
