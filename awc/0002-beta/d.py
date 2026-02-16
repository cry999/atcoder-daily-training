N, M = map(int, input().split())
(*C,) = map(int, input().split())
(*R,) = map(int, input().split())

C.sort(reverse=True)
R.sort(reverse=True)

i, j = 0, 0
cnt = 0
while i < N and j < M:
    if R[j] >= C[i]:
        # 開けられる
        cnt += 1
        j += 1
    # 開けられなくても宝箱は次に挑戦する
    i += 1

print(cnt)
