r, c = map(int, input().split())
senbei = [list(map(int, input().split())) for _ in range(r)]

ans = 0
for bit in range(1 << r):
    # 横を一斉にひっくり返すとどうなるか
    # bit & (1 << i) なら i 行目はひっくり返っている。

    score = 0
    for j in range(c):
        # 横の操作が終わっていると仮定して、この列をひっくり返すのが得か?
        not_reverse = 0
        for i in range(r):
            if bit & (1 << i):
                not_reverse += senbei[i][j] == 1
            else:
                not_reverse += senbei[i][j] == 0
        score += max(not_reverse, r - not_reverse)
    ans = max(ans, score)
print(ans)
