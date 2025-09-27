def s(n: int) -> str:
    if n == 1:
        return '1'
    s_n_1 = s(n - 1)
    return ' '.join([s_n_1, str(n), s_n_1])


N = int(input())
print(s(N))
