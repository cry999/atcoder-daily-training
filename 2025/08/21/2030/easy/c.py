def equals(t, u):
    for i in range(len(u)):
        if t[i] != '?' and t[i] != u[i]:
            return False
    return True


T = input()
U = input()

for i in range(len(T)-len(U)+1):
    if equals(T[i:], U):
        print('Yes')
        exit()

print('No')
