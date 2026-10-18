N, M = map(int, input().split())

index = {}
votes = [0] * N
for i in range(N):
    s = input()
    index[s] = i


def get_index(s: str) -> int:
    candidates = []
    for name, idx in index.items():
        if name == s:
            return idx
        if len(name) == len(s) and sum(c1 != c2 for c1, c2 in zip(name, s)) == 1:
            candidates.append(idx)
    if len(candidates) == 1:
        return candidates[0]
    return -1


for _ in range(M):
    t = input()
    i = get_index(t)
    if i != -1:
        votes[i] += 1

print("\n".join(map(str, votes)))
