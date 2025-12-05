from math import comb

N = int(input())
*A, = map(int, input().split())
# A.sort()

MAX_A = max(A)

primes = []
factor = [1] * (MAX_A + 1)
for i in range(2, MAX_A+1):
    if factor[i] == 1:
        primes.append(i)
        factor[i] = i
    for p in primes:
        if i*p > MAX_A or p > factor[i]:
            break
        factor[i*p] = p


m = {}
for i in range(N):
    a = A[i]
    for p in primes:
        if p*p > a:
            break
        while not a % (p*p):
            a //= (p*p)
    # A[i] = a
    m[a] = m.get(a, 0)+1

# print(m)

cnt = 0
# まずは 0 を処理
if 0 in m:
    # 0 は自分以外の何とでもペアを組める
    cnt += N*m[0] - (m[0]*(m[0]+1))//2
# 残りを処理
# 残りは、自分以外の自分と同じ数とペアを組める
for k, v in m.items():
    if k == 0:
        continue
    if v < 2:
        continue
    cnt += comb(v, 2)

print(cnt)
