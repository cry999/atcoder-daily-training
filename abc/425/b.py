N = int(input())
A = list(map(int, input().split()))

for i in range(N):
    for j in range(i+1, N):
        if A[i] != -1 and A[j] != -1 and A[i] == A[j]:
            print("No")
            break
    else:
        continue
    break
else:
    print("Yes")
    ans = []
    used = {i: False for i in range(1, N + 1)}
    for a in A:
        used[a] = True
    for a in A:
        if a == -1:
            for i in range(1, N+1):
                if not used[i]:
                    ans.append(i)
                    used[i] = True
                    break
        else:
            ans.append(a)
    print(*ans)
