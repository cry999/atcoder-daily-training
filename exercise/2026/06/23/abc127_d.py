N, M = map(int, input().split())
(*cards,) = map(int, input().split())
cards.sort()

changes = []
for _ in range(M):
    remain, score = map(int, input().split())
    changes.append((score, remain))
changes.sort()

total_score = 0
for _ in range(N):
    if not changes:
        total_score += cards.pop()
    elif cards[-1] < changes[-1][0]:
        score, remain = changes.pop()
        if remain > 1:
            changes.append((score, remain - 1))
        total_score += score
    else:
        total_score += cards.pop()
print(total_score)
