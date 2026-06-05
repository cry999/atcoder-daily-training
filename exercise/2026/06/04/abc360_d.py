N, T = map(int, input().split())
S = input()
(*X,) = map(int, input().split())

A = sorted(X[i] for i in range(N) if S[i] == "1")
B = sorted(X[i] for i in range(N) if S[i] == "0")

head, tail = 0, 0
ans = 0
for a in A:
    while head < len(B) and B[head] <= a:
        head += 1
    tail = max(tail, head)
    while tail < len(B) and B[tail] <= a + 2 * T:
        tail += 1
    ans += tail - head
print(ans)
