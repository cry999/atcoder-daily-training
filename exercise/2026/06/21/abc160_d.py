N, X, Y = map(int, input().split())


ans = [0] * N


def add_cycle(n: int):
    """
    n 個の頂点からなるサイクル上の頂点対の最短経路を加算する。
    距離 d の頂点対は、(i, i+d) を考えることで、n 個の組み合わせがある。
    (i+d は n を超える場合は、i+d-n として考える。)
    ただし、n が偶数のときは、d = n // 2 の頂点対は (i, i+d) が (i+d, i+2*d)
    と被ってしまうので、n // 2 個の組み合わせしかない。
    """
    for d in range(1, n // 2 + 1):
        if 2 * d == n:
            ans[d] += n // 2
        else:
            ans[d] += n


def add_line(n: int):
    """
    n 個の頂点からなる直線上の頂点対の最短経路を加算する。
    直線での最短経路ごとの頂点対の組数は、
    d = 1     -> n - 1
    d = 2     -> n - 2
    ...
    d = n - 2 -> 2
    d = n - 1 -> 1
    となっていることに注意する。
    """
    for d in range(1, n):
        ans[d] += n - d


def add_tail_and_cycle(tail_length: int, cycle_length: int):
    """
    しっぽ部分の頂点と、サイクル部分の頂点対を加算する。

    しっぽの付け根から距離 p の頂点と、サイクル上で付け根から距離 d の頂点を考えると、
    最短経路の長さは p + d になる。
    """

    # 最短経路の距離が d である頂点対を累積和で数える。
    diff = [0] * (N + 1)

    for p in range(1, tail_length + 1):
        # 付け根から距離 1 ~ (cycle_length - 1) // 2 の頂点は 2 個ずつある
        # 付け根自身との組み合わせは add_line で計上するので、ここでは p + 1 から考える。
        if p + 1 <= p + (cycle_length - 1) // 2:
            diff[p + 1] += 2
            diff[(cycle_length - 1) // 2 + p + 1] -= 2
        # ただし、サイクルの長さが偶数のときは、付け根からみて距離 cycle_length // 2 の頂点は 1 個しかない
        if cycle_length % 2 == 0:
            diff[cycle_length // 2 + p] += 1
            diff[cycle_length // 2 + p + 1] -= 1

    cur = 0
    for i in range(1, N):
        cur += diff[i]
        ans[i] += cur


def add_between_tails(left_tail: int, right_tail: int):
    """
    長さ left_tail と right_tail の直線部分の頂点対の最短経路を加算する。
    左側の X から p の距離の頂点と右側の頂点が q の頂点の長さは p + q + 1 になる。
    NOTE: +1 は X と Y の距離。

    p = 1, 2, ..., left_tail
    q = 1, 2, ..., right_tail

    となるので、最短経路の長さは 3 ~ left_tail + right_tail + 1 になる。

    ここで、s = p+q を固定して考えると、頂点対の組み合わせは
    (p, q) = (1, s-1), (2, s-2), ..., (s-1, 1) となる。
    """
    for s in range(2, left_tail + right_tail + 1):
        # s := p + q
        lo = max(1, s - right_tail)  # p の最小値
        hi = min(left_tail, s - 1)  # p の最大値

        # lo <= p <= hi の範囲なら対応する q が存在する
        ans[s + 1] += max(0, hi - lo + 1)


left_tail_length = X - 1
right_tail_length = N - Y
cycle_length = Y - X + 1

# 1. 左のしっぽ(+X)部分の頂点対の最短経路を加算する。
add_line(left_tail_length + 1)

# 2. 左のしっぽ部分の頂点と、サイクル部分の頂点対の最短経路を加算する。
add_tail_and_cycle(left_tail_length, cycle_length)

# 3. 右のしっぽ(+Y)部分の頂点対の最短経路を加算する。
add_line(right_tail_length + 1)

# 4. 右のしっぽ部分の頂点と、サイクル部分の頂点対の最短経路を加算する。
add_tail_and_cycle(right_tail_length, cycle_length)

# 5. しっぽ部分をまたいで、1~X と Y~N の組み合わせの最短経路を加算する。
add_between_tails(left_tail_length, right_tail_length)

# 6. 最後に、サイクル部分の頂点対の最短経路を加算する。
add_cycle(cycle_length)


for i in range(1, N):
    print(ans[i])
