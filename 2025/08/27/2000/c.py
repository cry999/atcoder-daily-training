def to_num(s):
    if s == 'A':
        return 0
    if s == 'B':
        return 1
    if s == 'C':
        return 2
    if s == 'D':
        return 3
    return 4  # 'E'


S1, S2 = map(to_num, input())
T1, T2 = map(to_num, input())

s, t = abs(S1-S2), abs(T1-T2)

if s in (1, 4) and t in (1, 4):
    print('Yes')
elif s in (2, 3) and t in (2, 3):
    print('Yes')
else:
    print('No')
