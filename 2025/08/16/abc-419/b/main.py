bag = []

Q = int(input())

for _ in range(Q):
    query = input()
    split = query.split(' ')
    if len(split) == 2:
        x = int(split[1])
        bag.append(x)
    else:
        pop = min(bag)
        del bag[bag.index(pop)]
        print(pop)
