T, M = map(int, input().split())

memo = [[0] * 5001 for _ in range(5001)]
memo[0][0] = 1

for n in range(1, 5001):
    memo[n][0] = 1
    for r in range(1, n+1):
        memo[n][r] = (memo[n-1][r-1] + memo[n-1][r]) % M

for _ in range(T):
    N = int(input())
    C = list(map(int, input().split()))

    total = sum(C)
    ans = 1
    for c in C:
        # print(f'{total=}, {c=}')
        # print(f'{ans}*{memo[total][c]}={ans*memo[total][c]}')
        ans *= memo[total][c]
        ans %= M
        total -= c
    print(ans)
