N = int(input())
(*A,) = map(lambda x: int(x) - 1, input().split())
rev = {a: i for i, a in enumerate(A)}

ans = []
for i in range(N):
    a = A[i]
    if i == a:
        continue
    # j: i がある index
    j = rev[i]
    ans.append((i + 1, j + 1))
    A[i], A[j] = A[j], A[i]
    rev[A[i]] = i
    rev[A[j]] = j

print(len(ans))
for i, j in ans:
    print(i, j)
