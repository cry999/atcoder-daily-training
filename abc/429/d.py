N, M, C = map(int, input().split())
*A, = sorted(map(lambda x: x if x else M, map(int, input().split())))

# B: 人が立っている地点 / P: その地点に立っている人の数
B, P = [], []
prev, K = 0, 0
for a in A:
    if prev != a:
        B.append(a)
        P.append(1)
        K += 1
        prev = a
    else:
        P[-1] += 1

ans = 0
Y, cur = 0, 0
for i in range(K):
    while Y < C:
        Y += P[cur]
        cur = (cur+1) % K

    # print(f'Y{i}:', Y)
    if i == 0:
        # Y1 は 0~B[0] と B[K-1]~M の間でスタートした場合の Xi の値。
        # したがって、B[0]+(M-B[K-1]) 回分 Y を足す。
        ans += (B[0] + (M-B[K-1])) * Y
    else:
        # i 回目は B[i-1]~B[i] の間でスタートした場合の Xi の値。
        # したがって、B[i]-B[i-1] 回分 Y を足す。
        ans += (B[i]-B[i-1]) * Y

    Y -= P[i]

print(ans)
