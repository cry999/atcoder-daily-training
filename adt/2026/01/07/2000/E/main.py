N, M, H, K = map(int, input().split())
S = input()
items = set([tuple(map(int, input().split())) for _ in range(M)])

x, y = 0, 0
for i in range(N):
    if S[i] == "R":
        x += 1
    if S[i] == "L":
        x -= 1
    if S[i] == "U":
        y += 1
    if S[i] == "D":
        y -= 1

    H -= 1
    # print(f"Step {i+1} / HP: {H} / ({x}, {y})")
    if H < 0:
        print("No")
        break

    if (x, y) in items and H < K:
        H = K
        items.remove((x, y))
else:
    print("Yes")
