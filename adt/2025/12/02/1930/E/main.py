*scores, = map(int, input().split())

alpha = 'ABCDE'
ranks = []
for bit in range(1, 1 << 5):
    name, score = '', 0
    for i in range(5):
        if (bit >> i) & 1:
            name += alpha[i]
            score += scores[i]
    ranks.append((-score, name))

ranks.sort()
for inv_score, name in ranks:
    print(name)
