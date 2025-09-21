N = int(input())

nexts = [[] for _ in range(N)]
acquired = []
skill = [False] * N

for i in range(N):
    A, B = map(int, input().split())
    if A == B == 0:
        acquired.append(i)
        skill[i] = True
    else:
        if A-1 != i:
            nexts[A-1].append(i)
        if B-1 != i and B != A:
            nexts[B-1].append(i)

while acquired:
    # print('acquired', acquired)
    s = acquired.pop()
    for ns in nexts[s]:
        if skill[ns]:
            continue
        skill[ns] = True
        acquired.append(ns)

# print(skill)
# print(nexts)
print(sum(skill))
