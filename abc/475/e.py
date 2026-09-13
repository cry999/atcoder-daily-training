import sys
from sortedcontainers import SortedList

input = sys.stdin.readline

N, M, K = map(int, input().split())
T = input().strip()

S = []
for _ in range(N):
    s = input().strip()
    S.append("".join("1" if a == b else "0" for a, b in zip(s, T)))

SS = SortedList(S)
zero = "0" * K

Q = int(input())
ans = []

for _ in range(Q):
    i, j = map(int, input().split())
    i -= 1
    j -= 1

    s = S[i]
    changed = s[:j] + ("0" if s[j] == "1" else "1") + s[j + 1 :]

    SS.remove(s)
    SS.add(changed)
    S[i] = changed

    # 本人を含め、changed 以上の人数
    cnt = N - SS.bisect_left(changed)

    ans.append(changed != zero and cnt <= M)

print("\n".join(map(lambda x: "Yes" if x else "No", ans)))
