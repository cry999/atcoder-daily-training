N, M, K = map(int, input().split())
(*A,) = map(int, input().split())

calory = 0
ans = [False] * N
for i in range(N):
    if i >= M and ans[i - M]:
        calory -= A[i - M]
    if calory + A[i] <= K:
        print("Yes")
        calory += A[i]
        ans[i] = True
    else:
        print("No")

    # print(f"[DEBUG] {calory=}")
