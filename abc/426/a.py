def f(s: str) -> int:
    if s == 'Ocelot':
        return 0
    elif s == 'Serval':
        return 1
    return 2


X, Y = map(f, input().split())
print('Yes' if X >= Y else 'No')
