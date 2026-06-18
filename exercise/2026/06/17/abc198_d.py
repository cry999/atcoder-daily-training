from itertools import permutations

S1 = input()
S2 = input()
S3 = input()

N1 = len(S1)
N2 = len(S2)
N3 = len(S3)

m = {}
for c in S1 + S2 + S3:
    if c not in m:
        m[c] = len(m)

if len(m) > 10:
    print("UNSOLVABLE")
else:
    for perm in permutations(range(10), len(m)):

        def number(S: str):
            s = 0
            for c in S:
                s = s * 10 + perm[m[c]]
            return s

        if perm[m[S1[0]]] == 0 or perm[m[S2[0]]] == 0 or perm[m[S3[0]]] == 0:
            continue

        s1 = number(S1)
        s2 = number(S2)
        s3 = number(S3)

        if s1 + s2 != s3:
            continue

        print(s1)
        print(s2)
        print(s3)
        break
    else:
        print("UNSOLVABLE")
