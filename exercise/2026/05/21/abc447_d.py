from collections import deque

S = input()

qa = deque()
qb = deque()
qc = deque()

for i, s in enumerate(S):
    if s == "A":
        qa.append(i)
    elif s == "B":
        qb.append(i)
    else:
        qc.append(i)

# should remove
rqa = deque()
rqb = deque()
rqc = deque()

ans = 0
while qa and qb and qc:
    ia = qa.popleft()

    while qb and qb[0] < ia:
        qb.popleft()
    if not qb:
        break
    ib = qb.popleft()

    while qc and qc[0] < ib:
        qc.popleft()
    if not qc:
        break
    ic = qc.popleft()

    rqa.append(ia)
    rqb.append(ib)
    rqc.append(ic)

    ans += 1

print(ans)
