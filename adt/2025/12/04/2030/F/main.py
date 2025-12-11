# 尺取法っぽい

N = int(input())
*P, = map(int, input().split())


i, cnt = 0, 0
while i <= N-4:
    if P[i] > P[i+1]:
        # P[i] < P[i+1] になる位置に移動する。
        # P[i] == P[i+1] はあり得ないので考慮しない。
        i += 1
        continue
    # P[i] < P[i+1] を満たしている場合

    # 山と谷の位置を覚えておく。
    # 山と谷がこの順番に 1 つずつ出現する限り j を増やしながら count する。
    mount, valley = -1, -1
    j = i+1

    while j < N-1 and P[j] < P[j+1]:
        # 山頂まで j を進める。
        j += 1
    if j == N-1:
        # 頂上がなく終了
        break
    # 今 j が山頂(P[j-1] < P[j] > P[j+1])
    mount = j

    while j < N-1 and P[j] > P[j+1]:
        # 谷底まで j を進める。
        j += 1
    if j == N-1:
        # 谷底がなく終了
        break
    # 今 j が谷底(P[j-1] > P[j] < P[j+1])
    valley = j
    i_cnt, j_cnt = 0, 0

    # 「山と谷が存在する => 連続部分列の長さは 4 以上」なので、長さの調節はしない。

    # あとは、上りである限り j を進めながら count up する。
    while j < N-1 and P[j] < P[j+1]:
        j += 1
        j_cnt += 1

    # 限界まで j を進めたら、今度は条件を満たす限り i を増やして count する。
    while P[i] < P[i+1]:
        i += 1
        i_cnt += 1

    # とりうる (i, j) の組み合わせの数を cnt に加算する。
    cnt += i_cnt * j_cnt

print(cnt)
