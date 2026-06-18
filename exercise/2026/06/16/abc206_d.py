N = int(input())
(*A,) = map(int, input().split())

max_a = max(A)

convert = [i for i in range(max_a + 1)]
op = 0

for i in range(N // 2):
    j = N - 1 - i

    ai = A[i]
    while ai != convert[ai]:
        ai = convert[ai]
    convert[A[i]] = ai

    aj = A[j]
    while aj != convert[aj]:
        aj = convert[aj]
    convert[A[j]] = aj

    if ai != aj:
        convert[ai] = aj
        op += 1

print(op)
