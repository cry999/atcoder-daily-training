N, K, X = map(int, input().split())
S = [input() for _ in range(N)]

A = []
for i1 in range(N):
    s1 = S[i1]
    if K == 1:
        A.append(s1)
        continue
    for i2 in range(N):
        s2 = s1+S[i2]
        if K == 2:
            A.append(s2)
            continue
        for i3 in range(N):
            s3 = s2+S[i3]
            if K == 3:
                A.append(s3)
                continue
            for i4 in range(N):
                s4 = s3+S[i4]
                if K == 4:
                    A.append(s4)
                    continue
                for i5 in range(N):
                    A.append(s4+S[i5])

A.sort()
print(A[X-1])
