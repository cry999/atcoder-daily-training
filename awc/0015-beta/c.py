N = int(input())

players: dict[int, list[int]] = {}

for _ in range(N):
    p, q = map(int, input().split())
    if p not in players:
        players[p] = []
    players[p].append(q)

ans = 0
for competition, teams in players.items():
    teams.sort()
    # print(f"{competition=}, {teams=}")
    i = 0
    n = len(teams)
    while i < len(teams):
        q = teams[i]
        j = 0

        while i + j < len(teams) and teams[i + j] == q:
            j += 1
            n -= 1

        i += j
        # print(f"  {i=}, {j=}, {n=}")
        ans += j * n

print(ans)
