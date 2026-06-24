N = int(input())
(*queue,) = filter(lambda x: x <= N, [357, 375, 537, 573, 735, 753])
s = set(queue)

for n in queue:
    d = 1
    while 10 * n >= d:
        q, r = divmod(n, d)

        print(f"[DEBUG] {n=} {d=}")
        a = q * d * 10 + 3 * d + r
        print(f"[DEBUG] {a=}")
        if a not in s and a <= N:
            queue.append(a)
            s.add(a)
        b = q * d * 10 + 5 * d + r
        print(f"[DEBUG] {b=}")
        if b not in s and b <= N:
            queue.append(b)
            s.add(b)
        c = q * d * 10 + 7 * d + r
        print(f"[DEBUG] {c=}")
        if c not in s and c <= N:
            queue.append(c)
            s.add(c)
        d *= 10
print(len(s))
