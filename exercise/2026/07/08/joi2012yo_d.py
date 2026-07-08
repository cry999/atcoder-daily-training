MOD = 10_000

N, K = map(int, input().split())

schedule = [0] * (N + 1)
for _ in range(K):
    day, pasta = map(int, input().split())
    schedule[day] = pasta

TOMATO = 1
CREAM = 2
BAZIL = 3

dp = [[0] * 4 for _ in range(4)]
dp[0][0] = 1

for day in range(1, N + 1):
    ndp = [[0] * 4 for _ in range(4)]

    for pasta in range(1, 4):
        if schedule[day] != 0 and schedule[day] != pasta:
            continue

        for last1 in range(4):
            for last2 in range(4):
                if pasta == last1 == last2:
                    continue
                ndp[last2][pasta] += dp[last1][last2]

    dp = [[x % MOD for x in ndp[i]] for i in range(4)]

print(sum(sum(r) % MOD for r in dp) % MOD)
