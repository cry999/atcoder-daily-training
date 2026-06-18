K = int(input())

S = input()
T = input()

remain = [K] * 10
remain[0] = 0

t_hand = [0] * 10
a_hand = [0] * 10

for i in range(4):
    remain[int(S[i])] -= 1
    remain[int(T[i])] -= 1

    t_hand[int(S[i])] += 1
    a_hand[int(T[i])] += 1

pow10 = [1] * 6
for i in range(5):
    pow10[i + 1] = pow10[i] * 10


def score(hand: list[int]):
    return sum(i * pow10[hand[i]] for i in range(10))


win = 0
total = 0
for t_card in range(1, 10):
    if remain[t_card] == 0:
        continue

    remain[t_card] -= 1
    t_hand[t_card] += 1

    t_score = score(t_hand)

    for a_card in range(1, 10):
        if remain[a_card] == 0:
            continue

        remain[a_card] -= 1
        a_hand[a_card] += 1

        a_score = score(a_hand)

        c = 0
        if t_card == a_card:
            c = (remain[t_card] + 2) * (remain[a_card] + 1)
        else:
            c = (remain[t_card] + 1) * (remain[a_card] + 1)

        total += c
        if t_score > a_score:
            win += c

        remain[a_card] += 1
        a_hand[a_card] -= 1

    remain[t_card] += 1
    t_hand[t_card] -= 1

print(win / total)
