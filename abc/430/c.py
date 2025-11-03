N, A, B = map(int, input().split())
S = input()

cum_a, cum_b = [0]*(N+1), [0]*(N+1)
for i, s in enumerate(S):
    if s == 'a':
        cum_a[i+1] = cum_a[i] + 1
        cum_b[i+1] = cum_b[i]
    else:
        cum_a[i+1] = cum_a[i]
        cum_b[i+1] = cum_b[i] + 1

count = 0
for left in range(N-A+1):
    # left を固定した時の条件を満たす right の最大・最小値を求める
    # これは二分探索で求められる.

    # right の最小値を求める。
    # 1. right >= left+A-1
    # 2. num_a < A なら right を大きくする
    # 3. num_b >= B なら right を小さくする。
    # 4. num_a < A かつ num_b >= B なら探索を失敗で終了

    lo, hi = left+A-1, N
    while lo < hi:
        mid = (lo+hi)//2
        num_a = cum_a[mid] - cum_a[left]
        num_b = cum_b[mid] - cum_b[left]
        if num_a < A and num_b >= B:
            lo, hi = -1, -1
            break
        elif num_a >= A:
            hi = mid
        else:  # num_a < A and num_b < B
            lo = mid + 1

    if lo < left+A-1:
        # print(f'not found because min_right({lo=}) < left+A-a-1')
        continue
    num_a, num_b = cum_a[lo] - cum_a[left], cum_b[lo] - cum_b[left]
    if num_a < A or num_b >= B:
        continue

    min_right = lo

    # print(f'{left=}, {lo=}')

    # right の最大値を求める。
    # 1. right >= left+A-1
    # 2. num_a >= A なら right を大きくする
    # 3. num_b >= B なら right を小さくする。
    # 4. num_a < A かつ num_b >= B なら探索を失敗で終了
    lo, hi = left+A-1, N
    while lo < hi:
        mid = (lo+hi+1)//2
        num_a = cum_a[mid] - cum_a[left]
        num_b = cum_b[mid] - cum_b[left]
        if num_a < A and num_b >= B:
            lo, hi = -1, -1
            break
        elif num_b < B:
            lo = mid
        else:
            hi = mid - 1

    if lo < left+A-1:
        # print(f'not found because max_right({lo=}) < left+A-a-1')
        continue
    num_a, num_b = cum_a[lo] - cum_a[left], cum_b[lo] - cum_b[left]
    if num_a < A or num_b >= B:
        continue

    # print(f'{left=}, {lo=}')
    max_right = lo
    # print(f'{left=}, {min_right=}, {max_right=}')
    count += max_right-min_right+1
print(count)
