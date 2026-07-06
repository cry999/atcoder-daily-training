N = int(input())
(*S,) = map(int, input())


ans = 0

# 高々 1000 通りの組み合わせしかないはず
check_1 = [False] * 10  # 一番左の数字
for i in range(N):
    if check_1[S[i]]:
        # 一度チェックしたものは再チェック不要
        continue
    check_1[S[i]] = True

    check_2 = [False] * 10  # 真ん中の数字
    for j in range(i + 1, N):
        if check_2[S[j]]:
            continue
        check_2[S[j]] = True

        check_3 = [False] * 10  # 一番右の数字
        for k in range(j + 1, N):
            if check_3[S[k]]:
                continue
            check_3[S[k]] = True

            ans += 1

print(ans)
