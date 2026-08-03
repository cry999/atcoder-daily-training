N = int(input())
S = input()

ans = [0] * N

right = 0
num_x = 0
for k in range(1, N + 1):
    while right < N and num_x < k:
        num_x += S[right] == "x"
        right += 1

    ans[k - 1] = right

print("\n".join(map(str, ans)))
