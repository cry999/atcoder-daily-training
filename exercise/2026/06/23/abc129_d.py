H, W = map(int, input().split())
S = [input() for _ in range(H)]

width = [0] * (H * W)
height = [0] * (H * W)

ans = 1
for h in range(H):
    for w in range(W):
        if S[h][w] == "#":
            continue
        pos = h * W + w
        if width[pos] == 0:
            sw = 1
            for ww in range(w + 1, W):
                if S[h][ww] == "#":
                    break
                sw += 1
            for ww in range(w, W):
                if S[h][ww] == "#":
                    break
                width[h * W + ww] = sw
        if height[pos] == 0:
            sh = 1
            for hh in range(h + 1, H):
                if S[hh][w] == "#":
                    break
                sh += 1
            for hh in range(h, H):
                if S[hh][w] == "#":
                    break
                height[hh * W + w] = sh

        ans = max(ans, width[pos] + height[pos] - 1)
print(ans)
