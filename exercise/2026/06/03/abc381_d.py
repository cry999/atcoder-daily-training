N = int(input())
(*A,) = map(int, input().split())

used = [False] * (N + 1)

ans = 0

# 偶数桁始まりと奇数桁始まりで確かめる
for head in range(0, 2):
    tail = head
    while head < N:
        tail = max(head, tail)
        while tail + 1 < N and A[tail] == A[tail + 1] and not used[A[tail]]:
            used[A[tail]] = True
            tail += 2

        # print(tail, head)
        ans = max(ans, tail - head)
        used[A[head]] = False
        head += 2


print(ans)
