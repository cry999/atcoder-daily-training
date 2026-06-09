def generate_321_like_number(n: int, d: int):
    """先頭の桁が n で d 桁の 321-like number を生成します"""
    if d <= 0:
        return

    if d == 1:
        yield n
        return

    a = n * 10 ** (d - 1)
    for i in range(n):
        for f in generate_321_like_number(i, d - 1):
            yield f + a


K = int(input())
n, d = 1, 1
while True:
    for a in generate_321_like_number(n, d):
        K -= 1
        if not K:
            print(a)
            break
    else:
        if n == 9:
            n, d = 1, d + 1
        else:
            n += 1
        continue
    break
