N = int(input())
(*A,) = map(int, input().split())
B = [0] * N

head = -1
for i in range(N):
    if A[i] == -1:
        head = i + 1
    else:
        B[A[i] - 1] = i + 1

C = []
while head:
    C.append(head)
    head = B[head - 1]

print(*C)
