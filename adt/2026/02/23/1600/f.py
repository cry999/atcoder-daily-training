from itertools import permutations

M = int(input())
S = [input() for _ in range(3)]

ans = -1
for i in range(10):
    # print(f"{i=}")
    c = f"{i}"
    # i: 揃える数字
    for s1, s2, s3 in permutations(range(3)):
        # s1, s2, s3 の順番で揃える
        t = 0
        for si in (s1, s2, s3):
            for j in range(M + 1):
                if j == 0 and si != s1:
                    # s1 以外は 0 秒で止められない
                    continue
                if S[si][(j + t) % M] == c:
                    t += j
                    break
            else:
                # S[si] には i が存在しないのでやっても無駄
                # print("  break")
                break
        else:
            # print(f"  {s1=}, {s2=}, {s3=}: {t=}")
            if ans == -1 or ans > t:
                ans = t
            continue
        break

print(ans)
