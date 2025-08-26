H = int(input())

h, i = 0, 0
while h <= H:
    h += 1 << i
    i += 1
    # print(h, i)

print(i)
