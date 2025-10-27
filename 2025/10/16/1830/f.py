N = int(input())
S = input()

max_seq = {}
cur, cnt = S[0], 1
for c in S[1:]+'-':
    if c == cur:
        cnt += 1
    else:
        max_seq[cur[0]] = max(max_seq.get(cur[0], 0), cnt)
        cur, cnt = c, 1

print(sum(max_seq.values()))
