N = int(input())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

ans_eq, ans_ne = 0, 0
for i in range(N):
    for j in range(N):
        if A[i] == B[j]:
            ans_eq += i == j
            ans_ne += i != j

print(ans_eq)
print(ans_ne)
