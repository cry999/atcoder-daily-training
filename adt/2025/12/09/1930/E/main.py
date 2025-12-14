N, K = map(int, input().split())
S = input()

one_ranges = []
lo, hi = 0, 0
while lo < N:
    while lo < N and S[lo] != '1':
        lo += 1
    if lo == N:
        break

    hi = lo
    while hi+1 < N and S[hi+1] == '1':
        hi += 1
    one_ranges.append((lo, hi))

    lo = hi+1

_, rk_1 = one_ranges[K-2]
lk, rk = one_ranges[K-1]
for i in range(N):
    if i <= rk_1:
        print(S[i], end='')
    elif i <= rk_1 + (rk-lk) + 1:
        print('1', end='')
    elif i <= rk:
        print('0', end='')
    else:
        print(S[i], end='')

print()
