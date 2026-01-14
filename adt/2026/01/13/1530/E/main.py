N, X, Y = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

A.sort(reverse=True)
B.sort(reverse=True)

sweetness = 0
salty = 0
ans = 0
for i in range(N):
    sweetness += A[i]
    salty += B[i]

    ans = i + 1

    if sweetness > X or salty > Y:
        break
print(ans)
