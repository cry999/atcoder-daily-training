# lipgloss の nested Render では外側 bg が内側 reset の先に届かない

## TL;DR

`lipgloss.Style.Render(s)` で `s` の中に既に Render 済みのセグメントが
含まれていると、各セグメントの末尾の `\033[0m` (全 attribute reset)
の後、外側スタイルの背景色 (background) は **自動再適用されない**。
結果、一見「外側 chunk 全体に bg を塗ったつもり」が、視覚上は
**bg を自前で持つ内側セグメントだけが塗られ、それ以外 (素の文字列や、
fg だけ持つ内側セグメント) は bg なしで出てしまう**。

行全体を均一に塗りたい場合は、**各セグメント (文字、罫線、空白) に
個別に bg 付きスタイルを当てて連結する** のが確実。

## 発生した状況

SBS diff の中央ブロック (`internal/ui/diff.go` の `renderSBCenter`) を、
当初は一括ラップで組み立てていた:

```go
bar := diffGutterStyle.Render("│")  // fg=Surface2, bg なし
as  := diffPlusLineNumStyle.Render(fmt.Sprintf("%3d", n))  // fg=overlay0, bg=diffPlusBg

rightChunk := bar + " " + as + " " + bar + " "
rightChunk = diffPlusLineStyle.Render(rightChunk)  // bg=diffPlusBg を全体に当てる "つもり"
```

期待: `│ N │ ` 全体が薄い緑 bg。
実際: `as` (= 行番号) だけ薄い緑 bg、`bar` と空白部分は **bg なし** で、
右側の罫線 (`outer │`) も bg なしで描画される。結果、ライン番号囲いの
両罫線のうち、論理的に「右側」にあるべき bg が「左側」だけにかかって
いるように見える、というユーザ報告につながった。

## 原因

`Style.Render` は ANSI シーケンスを以下のように吐く:

```
\033[<fg>;<bg>m <内容> \033[0m
```

末尾の `\033[0m` は **全 attribute (fg / bg / bold / ...) を一括 reset** する。

ここで `<内容>` に既に Render 済みの子セグメント (例えば `bar` の
`\033[<gutter-fg>m│\033[0m`) があると、子セグメント末尾の `\033[0m` で
外側の bg もリセットされ、その後の文字には **bg が乗らない** まま
出力される。

lipgloss は親 Render が子の reset を自動で「補修」しない (`\033[0m` を
親 bg の再開シーケンスに書き換えたり、`\033[49m` (bg-only reset) に
差し替えたりしない) 設計。

末尾パディング (`.Width(N).Render(s)` で生成される pad 部分) には
親 bg を自前で当ててくれるが、それは pad 専用の処理であって、子
セグメントの reset 跡を埋める処理ではない。

## 確認方法

ANSI を強制出力 (`CLICOLOR_FORCE=1`) して `od -c` で見ると、子の
`\033[0m` の直後に **親の `\033[fg;bgm` が再発行されていない** ことが
直接わかる:

```sh
CLICOLOR_FORCE=1 exercise test ... -s 2>&1 | sed -n '...' | od -c -An
```

修正後は各セグメントが自分の `\033[<fg>;<bg>m … \033[0m` を持つので、
隣接セグメントの bg コードがそのまま連続し、ターミナル上では bg が
途切れずに見える。

## 対策

**1. 行全体ラップではなく、セグメントごとに bg 付きスタイルを当てる。**

bar / 空白 / 数値など、構造上の各パーツに専用の bg 付きスタイルを定義し、
それらを **plain な文字列連結** で組む。外側からの一括ラップは使わない。

`internal/ui/style.go` で追加した bar 用 bg 付きスタイル:

```go
diffGutterStyle      = lipgloss.NewStyle().Foreground(Surface2)                    // bg なし
diffMinusGutterStyle = lipgloss.NewStyle().Foreground(Surface2).Background(MinusBg) // bg あり (minus 側)
diffPlusGutterStyle  = lipgloss.NewStyle().Foreground(Surface2).Background(PlusBg)  // bg あり (plus 側)
```

`renderSBCenter` での組み立て:

```go
leftSpace := diffMinusLineStyle.Render(" ")    // bg=MinusBg
leftBar   := diffMinusGutterStyle.Render("│")  // bg=MinusBg
// 連結すると bg が連続して見える
leftChunk := leftSpace + leftBar + leftSpace + es + leftSpace + leftBar
```

**2. それでも一括ラップしたい場合**

末尾までを `Background` で塗る用途で `Style.Width(N).Render(s)` を
使うと、pad 部分には親 bg が乗る。内側の reset 跡は埋まらないが、
パディングが行末まで連続して描かれることだけは保証される。

行全体の bg を、内側セグメントを含めて完全に塗りたいときは方針 1
を取るしかない (内側を「bg なしの素の文字列」だけで構成するなら
別、つまり `\033[0m` を含む子 Render を内側に持ち込まないなら一括
ラップでも OK)。

## 同類の落とし穴

- `lineStyle.Render(s)` の `s` に `lipgloss.JoinHorizontal(...)` の
  結果を入れる場合も同様。join 内部で各要素が個別 Render されていれば、
  各要素末尾の reset 後の挙動を確認する必要がある。
- 自前で組んだ ANSI 文字列を `Render` に渡すのも同じ罠を踏む。bg を
  保ちたいなら、自前 ANSI 側でも `\033[0m` ではなく `\033[39m` (fg-only
  reset) や `\033[22m` (bold-only reset) を使う必要がある。

## 関連コミット

- `f5f7ff7` ui(diff): paint SBS center bg per segment to cover both line-num bars
