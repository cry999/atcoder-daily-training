# fixture: float の許容誤差比較を確認するための fixture。
#   入力: 任意
#   actual:   "3.141592653589793" (Python の math.pi)
#   expected: "3.141593" (小数 6 桁に丸めた値)
#   差: ~3.6e-9、AtCoder 慣習の 1e-6 許容なら PASS になる。
import math
_ = input()
print(math.pi)
