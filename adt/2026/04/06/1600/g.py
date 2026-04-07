N = int(input())
(*A,) = map(int, input().split())

# inc: A[i] を末尾とする広義短調増加列の長さ
inc = [1] * N
# dec: A[i] を先頭とする講義単調減少列の長さ
dec = [1] * N

for i in range(N - 1):
    inc[i + 1] = min(A[i + 1], inc[i] + 1)

for i in range(N - 1, 0, -1):
    dec[i - 1] = min(A[i - 1], dec[i] + 1)

# print(inc, dec)
ans = max(min(i, d) for i, d in zip(inc, dec))
print(ans)
