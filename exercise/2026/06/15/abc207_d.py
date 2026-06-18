from itertools import permutations

N = int(input())
S = set(tuple(map(int, input().split())) for _ in range(N))
T = [tuple(map(int, input().split())) for _ in range(N)]

if N == 1:
    print("Yes")
    exit()


c1, d1 = T[0]
c2, d2 = T[1]

dc = c2 - c1
dd = d2 - d1

dist_t = dc**2 + dd**2
for s1, s2 in permutations(S, 2):
    # T[0] -> S[i], T[1] -> S[j] を一致させる
    a1, b1 = s1
    a2, b2 = s2

    da = a2 - a1
    db = b2 - b1
    dist_s = da**2 + db**2

    # そもそも距離があってないと無理。
    if dist_s != dist_t:
        continue

    # 回転角度 (T[1] -> S[j])
    sin_theta = db * dc - da * dd
    cos_theta = da * dc + db * dd

    for c, d in T[2:]:
        a = (c - c1) * cos_theta - (d - d1) * sin_theta
        if a % dist_t:
            break
        a //= dist_t
        a += a1

        b = (c - c1) * sin_theta + (d - d1) * cos_theta
        if b % dist_t:
            break
        b //= dist_t
        b += b1

        if (a, b) not in S:
            break
    else:
        print("Yes")
        break
else:
    print("No")
