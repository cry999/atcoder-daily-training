N, M = map(int, input().split())
(*F,) = map(int, input().split())

check = [0] * M

for i in range(N):
    check[F[i] - 1] += 1

if all(c <= 1 for c in check):
    print("Yes")
else:
    print("No")

if all(c >= 1 for c in check):
    print("Yes")
else:
    print("No")
