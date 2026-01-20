from collections import defaultdict

S = input()
counts = defaultdict(int)
for c in S:
    counts[ord(c) - ord("a")] += 1

ans = 1 if any(v > 1 for v in counts.values()) else 0
n = len(S)
for c in range(26):
    n -= counts[c]
    ans += counts[c] * n
print(ans)
