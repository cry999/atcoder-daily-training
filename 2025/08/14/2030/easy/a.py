def is_11_22(s: str, n: int) -> bool:
    if n % 2 == 0:
        return False
    for i in range((n+1)//2 - 1):
        if s[i] != '1':
            return False
    if s[(n+1)//2 - 1] != '/':
        return False
    for i in range((n+1)//2, n):
        if s[i] != '2':
            return False
    return True


N = int(input())
S = input()

if is_11_22(S, N):
    print('Yes')
else:
    print('No')
