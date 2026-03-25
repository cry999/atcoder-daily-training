S = input()

cols = [
    [S[6]],
    [S[3]],
    [S[1], S[7]],
    [S[0], S[4]],
    [S[2], S[8]],
    [S[5]],
    [S[9]],
]

if S[0] == "1":
    print("No")
    exit()

for i, col in enumerate(cols):
    # col は少なくとも 1 つピンが立っている列
    if all(c == "0" for c in col):
        continue

    target_col = i
    for j in range(i + 1, len(cols)):
        col2 = cols[j]

        if all(c == "0" for c in col2):
            continue

        target_col = j
        break

    if target_col - i > 1:
        # 間に全てのピンが倒れている列があるなら Yes
        print("Yes")
        break
else:
    print("No")
