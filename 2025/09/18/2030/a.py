def is_1122(t: str) -> bool:
    if len(t) % 2 == 0:
        # print('violation len')
        return False
    for i in range(len(t) // 2):
        if t[i] != '1':
            # print('violation 1')
            return False
    if t[len(t) // 2] != '/':
        # print('violation /')
        return False
    for i in range(len(t) // 2 + 1, len(t)):
        if t[i] != '2':
            # print('violation 2')
            return False
    return True


N = int(input())
S = input()

print('Yes' if is_1122(S) else 'No')
