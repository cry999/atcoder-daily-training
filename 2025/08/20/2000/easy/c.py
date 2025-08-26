def is_weak_password(s: str) -> bool:
    if s[0] == s[1] == s[2] == s[3]:
        return True
    if (int(s[0])+1) % 10 == int(s[1]) \
            and (int(s[1])+1) % 10 == int(s[2]) \
            and (int(s[2])+1) % 10 == int(s[3]):
        return True
    return False


X = input()

if is_weak_password(X):
    print('Weak')
else:
    print('Strong')
