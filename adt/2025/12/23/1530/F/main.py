from itertools import permutations


M = int(input())
S1 = input()
S2 = input()
S3 = input()

ans = float("inf")
for c in "0123456789":
    # c で揃える。
    if c not in S1 or c not in S2 or c not in S3:
        continue

    for s1, s2, s3 in permutations([S1, S2, S3]):
        # s1 -> s2 -> s3 の順で止める。
        t1 = s1.index(c)
        t2 = (s2 + s2).index(c, t1 + 1)
        t3 = (s3 + s3 + s3).index(c, t2 + 1)
        ans = min(ans, t3)


if ans == float("inf"):
    print(-1)
else:
    print(ans)
