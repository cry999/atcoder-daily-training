N = int(input())
(*X,) = (int(x) // 2 for x in input().split())

for k in range(N):
    if k == 0 or k == N - 1:
        print(X[-1] - X[0])
        continue

    # 右と左、どっちに先に行くのが得かを考える。
    # 1. 右に行く場合、一つ右までの距離 + そこから 0 までの距離 + そこから N-1 までの距離
    ans = (X[k + 1] - X[k]) + max(X[k] - X[0], X[-1] - X[k + 1])
    # 2. 左に行く場合、一つ左までの距離 + そこから N-1 までの距離 + そこから 0 までの距離
    ans = min(ans, (X[k] - X[k - 1]) + max(X[-1] - X[k], X[k - 1] - X[0]))
    print(ans)
