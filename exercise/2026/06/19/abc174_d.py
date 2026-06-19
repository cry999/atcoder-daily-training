N = int(input())
C = list(input())

# 現在見ている部分より右にある R をカウント。
# ゼロになるまで処理する。
R = C.count("R")

w, r = 0, N - 1
ans = 0
while w < N and R:
    if C[w] == "W":
        while w < r and C[r] != "R":
            r -= 1

        if w < r and C[r] == "R":
            C[w], C[r] = C[r], C[w]
            R -= 1
            ans += 1
        else:
            C[w] = "R"
            ans += 1
    else:
        R -= 1

    w += 1
print(ans)
