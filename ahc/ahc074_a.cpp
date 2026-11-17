// 商品の可変クラスタと窓の役割を焼きなまし、二色ブロックを頻度順に組み直す。
// 次注文の期待費用には商品一覧だけを使い、未来の注文は読まない。
// 設計・比較結果: ahc/ahc074/README.md
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <string>
#include <tuple>
#include <vector>
using namespace std;
using U = uint64_t;
int pc(U x) { return __builtin_popcountll(x); }
int main(int argc, char **argv) {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, k, p, r;
  if (!(cin >> n >> k >> p >> r))
    return 0;
  vector<U> codes(p);
  vector<string> strings(p);
  for (int a = 0; a < p; a++) {
    cin >> strings[a];
    for (int j = 0; j < n; j++)
      if (strings[a][j] == '1')
        codes[a] |= U(1) << j;
  }
  int h = 16, steps = argc > 2 ? atoi(argv[2]) : 3000000;
  if (argc > 1 && atoi(argv[1]) >= 4)
    h = atoi(argv[1]);
  int bn = n - h, c = k - bn;
  U hm = (U(1) << h) - 1, cm = ~hm, flip = 0;
  for (int j = 0; j < n; j++) {
    int count = 0;
    for (U x : codes)
      count += x >> j & 1;
    if (count < p / 2)
      flip |= U(1) << j;
  }
  for (U &x : codes)
    x ^= flip;
  mt19937 rng(74);
  auto real = [&]() { return (rng() + 0.5) / 4294967296.0; };
  auto distance = [&](int a, int b) {
    U x = codes[a] ^ codes[b];
    return (~x & hm) ? pc(x & cm) : 999;
  };
  vector<tuple<int, int, int>> edges;
  for (int a = 0; a < p; a++)
    for (int b = 0; b < a; b++)
      if (~(codes[a] ^ codes[b]) & hm)
        edges.emplace_back(distance(a, b), a, b);
  sort(edges.begin(), edges.end());
  vector<int> used(p);
  vector<vector<int>> cl;
  for (auto [d, a, b] : edges)
    if (!used[a] && !used[b] && int(cl.size()) < p - c) {
      used[a] = used[b] = 1;
      cl.push_back({a, b});
    }
  for (int a = 0; a < p; a++)
    if (!used[a])
      cl.push_back({a});
  auto fallback = [&]() {
    for (int j = 0; j < n; j++)
      for (int col = 0; col < 2; col++) {
        string s(n, '.');
        s[j] = '0' + col;
        cout << s << '\n';
      }
    for (int z = 2 * n; z < k; z++)
      cout << string(n, '.') << '\n';
    cout.flush();
    vector<int> cur(n);
    for (int turn = 0; turn < r; turn++) {
      int a;
      if (!(cin >> a) || a < 0)
        return;
      vector<pair<int, int>> ans;
      for (int j = 0; j < n; j++)
        if (cur[j] != strings[a][j] - '0') {
          ans.emplace_back(2 * j + cur[j], 2 * j + 1);
          cur[j] ^= 1;
        }
      cout << ans.size() << '\n';
      for (auto [x, d] : ans)
        cout << x << ' ' << d << '\n';
      cout.flush();
    }
  };
  if (int(cl.size()) != c) {
    fallback();
    return 0;
  }
  vector<int> handles(h), content;
  iota(handles.begin(), handles.end(), 0);
  for (int j = h; j < n; j++)
    content.push_back(j);
  int maxsize = argc > 3 ? atoi(argv[3]) : 4;
  auto common = [&](const vector<int> &v) {
    U yes = ~U(0), no = 0;
    for (int a : v) {
      yes &= codes[a];
      no |= codes[a];
    }
    return yes | ~no;
  };
  auto clcost = [&](const vector<int> &v) {
    U base = ~U(0);
    int sum = 0;
    for (int a : v) {
      base &= codes[a];
      sum += pc(codes[a] & cm);
    }
    return sum - int(v.size()) * pc(base & cm);
  };
  int score = 0;
  for (auto &v : cl)
    score += clcost(v);
  int bestscore = score;
  auto bestcl = cl;
  U bestcm = cm, besthm = hm;
  for (int t = 0; t < steps; t++) {
    double progress = double(t) / steps;
    if (t % 25 == 0) {
      int xi = rng() % h, yi = rng() % bn, x = handles[xi], y = content[yi];
      int delta = 0;
      U nhm = hm ^ (U(1) << x) ^ (U(1) << y);
      bool valid = true;
      for (auto &v : cl) {
        U base = ~U(0);
        int nx = 0, ny = 0;
        for (int a : v) {
          base &= codes[a];
          nx += codes[a] >> x & 1;
          ny += codes[a] >> y & 1;
        }
        delta += nx - int(v.size()) * int(base >> x & 1) - ny +
                 int(v.size()) * int(base >> y & 1);
        if (!(common(v) & nhm)) {
          valid = false;
          break;
        }
      }
      double temp = 8 * pow(0.3 / 8, progress);
      if (valid && (delta <= 0 || real() < exp(-delta / temp))) {
        hm = nhm;
        cm = ~hm;
        swap(handles[xi], content[yi]);
        score += delta;
      }
    } else {
      int i = rng() % c, j = rng() % c;
      if (i == j)
        continue;
      auto oldi = cl[i], oldj = cl[j];
      int old = clcost(oldi) + clcost(oldj);
      if (rng() % 2) {
        int x = rng() % cl[i].size(), y = rng() % cl[j].size();
        swap(cl[i][x], cl[j][y]);
      } else {
        if (cl[i].size() < 2 || int(cl[j].size()) >= maxsize)
          continue;
        int x = rng() % cl[i].size();
        cl[j].push_back(cl[i][x]);
        cl[i].erase(cl[i].begin() + x);
      }
      int nv = clcost(cl[i]) + clcost(cl[j]), delta = nv - old;
      double temp = 1.5 * pow(0.03 / 1.5, progress);
      if ((common(cl[i]) & hm) && (common(cl[j]) & hm) &&
          (delta <= 0 || real() < exp(-delta / temp)))
        score += delta;
      else {
        cl[i] = oldi;
        cl[j] = oldj;
      }
    }
    if (score < bestscore) {
      bestscore = score;
      bestcl = cl;
      bestcm = cm;
      besthm = hm;
    }
  }
  cl = bestcl;
  cm = bestcm;
  hm = besthm;
  handles.clear();
  content.clear();
  for (int j = 0; j < n; j++)
    ((hm >> j & 1) ? handles : content).push_back(j);
  // 初期状態は白黒交互。その後は隣り合う 2 枚を常に異色に保つ。
  vector<int> sizes(h, c / (2 * h) * 2);
  int remainder = (c - accumulate(sizes.begin(), sizes.end(), 0)) / 2;
  for (int g = 0; g < remainder; g++)
    sizes[g] += 2;
  vector<array<vector<int>, 2>> slots(h);
  vector<vector<pair<int, int>>> choices(c);
  for (int i = 0; i < c; i++)
    for (int g = 0; g < h; g++) {
      int col = codes[cl[i][0]] >> handles[g] & 1;
      bool good = true;
      for (int a : cl[i])
        if (int(codes[a] >> handles[g] & 1) != col)
          good = false;
      if (good)
        choices[i].emplace_back(g, col);
    }
  function<bool(int, vector<int> &)> put = [&](int i, vector<int> &seen) {
    auto opts = choices[i];
    stable_sort(opts.begin(), opts.end(), [&](auto a, auto b) {
      return slots[a.first][a.second].size() * sizes[b.first] <
             slots[b.first][b.second].size() * sizes[a.first];
    });
    for (auto [g, col] : opts) {
      int gc = 2 * g + col;
      if (seen[gc])
        continue;
      seen[gc] = 1;
      auto &v = slots[g][col];
      if (int(v.size()) < sizes[g] / 2) {
        v.push_back(i);
        return true;
      }
      auto copy = v;
      for (int old : copy)
        if (put(old, seen)) {
          v.erase(find(v.begin(), v.end(), old));
          v.push_back(i);
          return true;
        }
    }
    return false;
  };
  vector<int> ids(c);
  iota(ids.begin(), ids.end(), 0);
  stable_sort(ids.begin(), ids.end(), [&](int a, int b) {
    return choices[a].size() < choices[b].size();
  });
  for (int i : ids) {
    vector<int> seen(2 * h);
    if (!put(i, seen)) {
      fallback();
      return 0;
    }
  }
  vector<U> masks, blacks;
  for (int j : content) {
    masks.push_back(U(1) << j);
    blacks.push_back(U(1) << j);
  }
  vector<vector<int>> groups(h);
  vector<int> member(p), loc(k);
  for (int g = 0; g < h; g++)
    for (int t = 0; t < sizes[g] / 2; t++)
      for (int col = 0; col < 2; col++) {
        int i = slots[g][col][t], item = masks.size();
        U base = ~U(0);
        for (int a : cl[i]) {
          base &= codes[a];
          member[a] = item;
        }
        U mask = cm | (U(1) << handles[g]);
        masks.push_back(mask);
        blacks.push_back(base & mask);
        groups[g].push_back(item);
        loc[item] = g;
      }
  for (int item = 0; item < k; item++) {
    string s(n, '.');
    for (int j = 0; j < n; j++)
      if (masks[item] >> j & 1)
        s[j] = '0' + ((blacks[item] ^ flip) >> j & 1);
    cout << s << '\n';
  }
  cout.flush();
  vector<int> weight(k);
  for (int item : member)
    weight[item]++;
  vector<U> need(p);
  vector<double> priority(bn);
  for (int a = 0; a < p; a++)
    need[a] = codes[a] & cm & ~blacks[member[a]];
  for (int item = 0; item < bn; item++) {
    int needed = 0, forbidden = 0;
    U bit = U(1) << content[item];
    for (int a = 0; a < p; a++) {
      needed += bool(need[a] & bit);
      forbidden += !(codes[a] & bit);
    }
    priority[item] = double(needed) / max(1, forbidden);
  }
  vector<int> order(k);
  iota(order.begin(), order.end(), 0);
  int current = -1;
  for (int turn = 0; turn < r; turn++) {
    int a;
    if (!(cin >> a) || a < 0)
      return 0;
    U target = codes[a];
    int page = member[a], g = loc[page];
    vector<pair<int, int>> ans;
    auto move = [&](int item, int d) {
      auto it = find(order.begin(), order.end(), item);
      order.erase(it);
      order.insert(order.begin() + d, item);
      ans.emplace_back(item, d);
    };
    // 先頭の色を反転する 1 移動を、重いページを手前へ残す配置変更と兼用する。
    auto flipgroup = [&](int group) {
      auto &v = groups[group];
      int item = v[0], at = 1, bestvalue = 100000;
      for (int t = 1; t < int(v.size()); t++) {
        auto next = v;
        rotate(next.begin(), next.begin() + 1, next.begin() + t + 1);
        bool valid = true;
        int value = 0;
        for (int ix = 0; ix < int(next.size()); ix++) {
          value += weight[next[ix]] * ix;
          if (ix % 2 == 1 &&
              !((blacks[next[ix]] ^ blacks[next[ix - 1]]) >> handles[group] &
                1))
            valid = false;
        }
        if (valid && value < bestvalue) {
          bestvalue = value;
          at = t;
        }
      }
      int d = find(order.begin(), order.end(), v[at]) - order.begin();
      move(item, d);
      rotate(v.begin(), v.begin() + 1, v.begin() + at + 1);
    };
    if (current >= 0) {
      int oldg = loc[current];
      if (oldg != g) {
        if ((blacks[current] ^ target) >> handles[oldg] & 1)
          flipgroup(oldg);
        else
          move(current, bn);
      } else if (current == page)
        move(current, bn);
    }
    // 取り出す途中の紙を、追加移動なしで頻度順の二色ブロックに組み直す。
    int rank =
        find(groups[g].begin(), groups[g].end(), page) - groups[g].begin();
    int end = (rank / 2 + 1) * 2;
    vector<int> colors[2];
    int pagecolor = blacks[page] >> handles[g] & 1;
    for (int ix = 0; ix < end; ix++)
      if (groups[g][ix] != page) {
        int item = groups[g][ix];
        colors[blacks[item] >> handles[g] & 1].push_back(item);
      }
    for (auto &v : colors)
      stable_sort(v.begin(), v.end(),
                  [&](int a, int b) { return weight[a] > weight[b]; });
    vector<int> desired{page, colors[1 - pagecolor][0]};
    colors[1 - pagecolor].erase(colors[1 - pagecolor].begin());
    vector<pair<int, int>> pairs;
    for (int ix = 0; ix < int(colors[0].size()); ix++) {
      int x = colors[0][ix], y = colors[1][ix];
      if (weight[x] < weight[y])
        swap(x, y);
      pairs.emplace_back(x, y);
    }
    stable_sort(pairs.begin(), pairs.end(), [&](auto a, auto b) {
      return weight[a.first] + weight[a.second] >
             weight[b.first] + weight[b.second];
    });
    for (auto [x, y] : pairs) {
      desired.push_back(x);
      desired.push_back(y);
    }
    bool placed[192] = {};
    placed[page] = true;
    if (rank % 2 == 0)
      placed[groups[g][rank + 1]] = true;
    vector<int> movable(groups[g].begin(), groups[g].begin() + rank);
    for (int item : movable) {
      int ix = find(desired.begin(), desired.end(), item) - desired.begin(),
          anchor = -1;
      for (int z = ix - 1; z >= 0; z--)
        if (placed[desired[z]]) {
          anchor = desired[z];
          break;
        }
      int d = find(order.begin(), order.end(), anchor) - order.begin();
      move(item, d);
      placed[item] = true;
    }
    copy(desired.begin(), desired.end(), groups[g].begin());
    // 必要紙を上げる費用と不要紙を下げる費用が最小になる位置へ挿す。
    U patches = target & cm & ~blacks[page];
    vector<int> bank(order.begin(), order.begin() + bn);
    int val = pc(patches), best = val, cut = 0;
    for (int t = 0; t < bn; t++) {
      U bit = U(1) << content[bank[t]];
      if (patches & bit)
        val--;
      else if (!(target & bit))
        val++;
      if (val < best) {
        best = val;
        cut = t + 1;
      }
    }
    // 現在の手数が同じ候補だけで、次の未知注文に対する条件付き期待費用を比較。
    vector<int> bestup, bestdown;
    long long bestfuture = 1LL << 60;
    set<vector<int>> evaluated;
    int current_product = a;
    int value = pc(patches);
    auto futurecost = [&](const vector<int> &next) {
      long long total = 0;
      for (int a = 0; a < p; a++) {
        if (a == current_product)
          continue;
        int score = pc(need[a]), best = score;
        for (int item : next) {
          U bit = U(1) << content[item];
          if (need[a] & bit)
            score--;
          else if (!(codes[a] & bit))
            score++;
          best = min(best, score);
        }
        total += best;
      }
      return total;
    };
    for (int t = 0; t <= bn; t++) {
      if (value == best) {
        vector<int> up, down, middle;
        for (int ix = 0; ix < bn; ix++) {
          int item = bank[ix];
          U bit = U(1) << content[item];
          if (ix >= t && (patches & bit))
            up.push_back(item);
          else if (ix < t && !(target & bit))
            down.push_back(item);
          else
            middle.push_back(item);
        }
        for (int sorted = 0; sorted < 2; sorted++) {
          if (sorted) {
            stable_sort(up.begin(), up.end(), [&](int a, int b) {
              return priority[a] < priority[b];
            });
            stable_sort(down.begin(), down.end(), [&](int a, int b) {
              return priority[a] > priority[b];
            });
          }
          vector<int> next(up.rbegin(), up.rend());
          next.insert(next.end(), middle.begin(), middle.end());
          next.insert(next.end(), down.begin(), down.end());
          if (!evaluated.insert(next).second)
            continue;
          long long estimate = futurecost(next);
          if (estimate < bestfuture) {
            bestfuture = estimate;
            cut = t;
            bestup = up;
            bestdown = down;
          }
        }
      }
      if (t < bn) {
        U bit = U(1) << content[bank[t]];
        if (patches & bit)
          value--;
        else if (!(target & bit))
          value++;
      }
    }
    int count = cut;
    for (int item : bestup) {
      move(item, 0);
      count++;
    }
    for (int item : bestdown) {
      move(item, bn - 1);
      count--;
    }
    move(page, count);
    current = page;
    for (int group = 0; group < h; group++)
      if (group != g &&
          ((blacks[groups[group][0]] ^ target) >> handles[group] & 1))
        flipgroup(group);
    cout << ans.size() << '\n';
    for (auto [x, d] : ans)
      cout << x << ' ' << d << '\n';
    cout.flush();
  }
}
