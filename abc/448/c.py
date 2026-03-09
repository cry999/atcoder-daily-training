N, Q = map(int, input().split())
(*A,) = map(int, input().split())
S = sorted(A)

for _ in range(Q):
    K = int(input())
    (*B,) = map(lambda x: A[int(x) - 1], input().split())
    B.sort()

    cur = 0
    for b in B:
        if S[cur] == b:
            cur += 1
            continue
        break

    print(S[cur])
