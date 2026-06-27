N = int(input())
(*A,) = map(int, input().split())

head, tail = 0, 0
s = 0
ans = 0
while head < N:
    tail = max(tail, head)
    while tail < N and s & A[tail] == 0:
        s ^= A[tail]
        tail += 1

    ans += tail - head

    s ^= A[head]
    head += 1
print(ans)
