from sortedcontainers import SortedSet
from collections import defaultdict

N = int(input())
X = SortedSet()
login_days = defaultdict(int)
logout_days = defaultdict(int)
for _ in range(N):
    A, B = map(int, input().split())
    login_days[A] += 1
    logout_days[A + B] += 1
    X.add(A)
    X.add(A + B)

people = 0
days = [0] * (N + 1)
for i in range(len(X) - 1):
    cur = X[i]
    nxt = X[i + 1]

    people += login_days[cur]
    people -= logout_days[cur]

    days[people] += nxt - cur

print(*days[1:])
