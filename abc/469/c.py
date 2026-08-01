N = int(input())
S = input()

ans = [0] * N

pre_o = [0] * (N + 1)
pre_x = [0] * (N + 1)
for i in range(N):
    pre_o[i + 1] = pre_o[i] + (S[i] == "o")
    pre_x[i + 1] = pre_x[i] + (S[i] == "x")

right = 0
for left in range(1, N + 1):
    right = max(right, left)

    if pre_x[left] == left:
        # 当たりがもらえなかったので進めない
        ans[left - 1] = 0
        continue

    while right < N and pre_x[right + 1] <= pre_o[left]:
        right += 1

    ans[left - 1] = right

print("\n".join(map(str, ans)))
