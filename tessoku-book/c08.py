N = int(input())
tickets = [tuple(map(int, input().split())) for _ in range(N)]
tickets.sort(key=lambda x: x[1])


def digit_diff_count(x: int, y: int) -> int:
    ''' x と y の異なる桁数を返す '''
    count = 0
    while x or y:
        count += x % 10 != y % 10
        x, y = x // 10, y // 10
    return count


if tickets[0][1] == 1:
    print(f'{tickets[0][0]:04}')
else:
    numbers = [True] * 10000
    count = 10000
    for s, t in tickets:
        if t == 2:  # t == 2 の時は s と 1 桁違いのものだけ残す
            for n, ok in enumerate(numbers):
                if not ok:
                    continue
                # 候補のなかで s と 1 桁違いのものだけ残す
                if digit_diff_count(n, s) == 1:
                    continue
                numbers[n] = False
                count -= 1
        else:  # t == 3 の時は s と異なる数の桁数が 0 or 1 のものは対象外
            for n, ok in enumerate(numbers):
                if not ok:
                    continue
                if digit_diff_count(n, s) > 1:
                    continue
                numbers[n] = False
                count -= 1
        if count == 1:
            print(*[f'{n:04}' for n, ok in enumerate(numbers) if ok])
            break
    else:
        print("Can't Solve")
