INF = 10**18


T = int(input())
for _ in range(T):
    N = int(input())
    # (クーポン不使用価格, クーポン使用価格)
    prices = [tuple(map(int, input().split())) for _ in range(N)]
    # クーポン不使用と使用の差額でソート
    prices.sort()
    prices.sort(key=lambda x: x[0] - x[1])

    min_price = INF
    for i in range(N):
        min_price = min(min_price, prices[i][0])

    all_coupon_price = sum(price[1] for price in prices)

    ans = INF
    normal_price = 0  # クーポンを使わないで購入するものの合計金額
    for k in range(N + 1):
        # クーポンを使わずに k 種類を購入する

        # 追加で必要なクーポンの枚数は最安商品を複数回買って処理する
        ex_coupon = max(0, N - 2 * k)
        ans = min(ans, all_coupon_price + normal_price + ex_coupon * min_price)
        if k < N:
            normal_price += prices[k][0] - prices[k][1]
    print(ans)
