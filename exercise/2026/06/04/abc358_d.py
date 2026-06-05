N, M = map(int, input().split())
(*A,) = sorted(map(int, input().split()))
(*B,) = sorted(map(int, input().split()))

i, j = 0, 0
ans = 0
while i < N and j < M:
    if A[i] >= B[j]:
        # j さんにお菓子 i を渡す
        ans += A[i]
        i += 1
        j += 1
    else:
        # お菓子 i を渡す相手はいない
        i += 1

if j < M:
    # お菓子が足りない
    print(-1)
else:
    # お菓子が足りている
    print(ans)
