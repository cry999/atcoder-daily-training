N = int(input())
(*A,) = map(int, input().split())

# 累積和でいけそう。 O(N)
# cum[A[i]] += 1
# cum[i] := 10^(A[i]-1) の位の数字
M = max(A)
cum = [0] * (2 * M + 1)
for a in A:
    cum[a - 1] += 1

for i in range(M - 1, 0, -1):
    cum[i - 1] += cum[i]

# 繰り上がり処理
for i in range(2 * M):
    cum[i + 1] += cum[i] // 10
    cum[i] %= 10

ans = []
for i in range(2 * M, -1, -1):
    if cum[i] == 0:
        continue
    for j in range(i, -1, -1):
        ans.append(str(cum[j]))
    break
print("".join(ans))
