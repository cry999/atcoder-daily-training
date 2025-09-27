# greedy
S = input()
T = ''

# 今みている文字より左に o よりも近くに # があるか
sharp = True
for c in S:
    if c == '#':
        T += '#'
        sharp = True
    elif c == '.':
        if sharp:
            T += 'o'
            sharp = False
        else:
            T += '.'

print(T)
