N = int(input())
A = sorted(map(int, input().split()), reverse=True)  # N
B = sorted(map(int, input().split()), reverse=True)  # N-1

i = j = 0
ans = 0
while i < N and i - j <= 1:
    if j == N - 1 and ans == 0:
        ans = A[i]
        break
    if A[i] <= B[j]:
        i += 1
        j += 1
    elif ans == 0:
        ans = A[i]
        i += 1
    else:
        ans = -1
        break

print(ans)
