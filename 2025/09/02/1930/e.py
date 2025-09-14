N = int(input())
H = list(map(int, input().split()))

T = 0
for i in range(N):
    # print('===', i, '===')
    # a から b までの間にある 3 の倍数の個数は (b - a + a%3)//3 個
    target = H[i]

    # i 番目の敵を倒したターン数を計算する。
    left, right = 1, 10**9
    while left <= right:
        mid = (left + right) // 2
        turns = mid  # 戦っているターン数
        start, end = T+1, T+mid
        turns_3_damage = (end - start + (start % 3)) // 3
        turns_1_damage = turns - turns_3_damage
        damage = turns_3_damage * 3 + turns_1_damage * 1
        # print(f'damage={
        #       damage}(3*{
        #       turns_3_damage} + 1*{turns_1_damage}) turn {start} to {end}')
        if damage > target:
            right = mid - 1
        elif damage < target:
            left = mid + 1
        else:
            right = mid
            break
    T += max(left, right)

print(T)
