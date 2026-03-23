N, T, A = map(int, input().split())
r = N - (T + A)
if r + T > N // 2 and r + A > N // 2:
    print("No")
else:
    print("Yes")
