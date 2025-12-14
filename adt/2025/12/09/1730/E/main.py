def reput(start=1):
    i = start
    yield i
    for _ in range(20):
        i = i*10 + 1
        yield i


*s, = sorted(a+b+c
             for a in reput()
             for b in reput(start=a)
             for c in reput(start=b)
             )

# print(len(s))
print(s[int(input())-1])
