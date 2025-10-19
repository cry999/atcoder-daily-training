Q = int(input())
cur = 0

open_brackets = []
paired_brackets = []
not_paired_brackets = []

for _ in range(Q):
    query = input().split()
    # print('---')
    # print(f'{cur=}')
    # print(f'{open_brackets=}')
    # print(f'{paired_brackets=}')
    # print(f'{not_paired_brackets=}')
    # print(f'{query=}')
    if query[0] == '1':
        if query[1] == '(':
            open_brackets.append(cur)
        else:
            if open_brackets:
                pair = open_brackets.pop()
                paired_brackets.append((cur, pair))
            else:
                not_paired_brackets.append(cur)
        cur += 1
    else:
        if open_brackets and open_brackets[-1] == cur-1:
            open_brackets.pop()
        elif paired_brackets and paired_brackets[-1][0] == cur-1:
            _, open_bracket = paired_brackets.pop()
            open_brackets.append(open_bracket)
        elif not_paired_brackets and not_paired_brackets[-1] == cur-1:
            not_paired_brackets.pop()
        cur -= 1
    if open_brackets or not_paired_brackets:
        print('No')
    else:
        print('Yes')
