H, W = map(int, input().split())

S = [list(input()) for _ in range(H)]

for s in S:
    for j in range(W-1):
        c1, c2 = s[j], s[j+1]
        if c1 == 'T' and c2 == 'T':
            s[j], s[j+1] = 'P', 'C'

print('\n'.join(''.join(s) for s in S))
