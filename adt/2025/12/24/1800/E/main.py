N = int(input())
(*a,) = map(int, input().split())
a.sort()

# まずは、読む用と売る用(だぶり)に分ける。
for_read = []
for_sale = []

i = 0
while i < N:
    for_read.append(a[i])

    i += 1
    while i < N and a[i] == for_read[-1]:
        for_sale.append(a[i])
        i += 1


read = []
i = 0
while i < len(for_read) or for_sale:
    # print(f"{i=}, {for_read=}, {for_sale=}, {read=}")
    if i < len(for_read) and for_read[i] == len(read) + 1:
        read.append(for_read[i])
        i += 1
    else:
        sold_count = 2
        while for_sale and sold_count:
            # まずは売る用から売っていく。
            for_sale.pop()
            sold_count -= 1

        while len(for_read) - i > 0 and sold_count:
            # 売る用で足りなければ読む用の大きい方から売っていく。
            for_read.pop()
            sold_count -= 1

        if sold_count:
            # それでも足りなければ終了。
            break
        # 足りたら読んだ本に追加して続行。
        read.append(len(read) + 1)

print(len(read))
