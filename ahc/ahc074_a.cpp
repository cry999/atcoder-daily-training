// 補助紙の期待手数と取得順位で設計し、各群の先頭2枚だけを異色に保つ。
// 次注文の期待費用には商品一覧だけを使い、未来の注文は読まない。
// 設計・比較結果: ahc/ahc074/README.md
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <ctime>
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
  clock_t design_start = clock();
  int h = 14, steps = argc > 2 ? atoi(argv[2]) : 6000000;
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
  int bias = argc > 5 ? atoi(argv[5]) : 12;
  // ランダムな補助紙順での最小cut期待値を16倍して丸める。実順序の代理評価。
  int expected[65][65];
  for (int u = 0; u <= 64; u++)
    for (int v = 0; v <= 64; v++) {
      int lo = min(u, v), hi = max(u, v);
      double value = lo, prob = 1;
      for (int z = 0; z < lo; z++) {
        prob *= double(lo - z) / (hi + z + 1);
        value -= prob;
      }
      expected[u][v] = lround(16 * value);
    }
  auto clcost = [&](const vector<int> &v) {
    U base = ~U(0);
    for (int a : v)
      base &= codes[a];
    int sum = 0;
    for (int a : v)
      sum += expected[pc(codes[a] & cm & ~base)][pc(~codes[a] & cm)];
    return sum;
  };
  auto totalcost = [&]() {
    int cost = 0;
    for (auto &v : cl)
      cost += clcost(v);
    return cost;
  };
  int score = 0;
  for (auto &v : cl)
    score += clcost(v);

  vector<int> hist(maxsize + 2);
  for (auto &v : cl)
    hist[v.size()]++;
  // 窓・色の制約を無視して重い紙から各群へ配る楽観的な順位費用。
  auto rankproxy = [&](const vector<int> &counts) {
    auto sumrank = [&](int t) {
      int q = t / h, rem = t % h;
      return h * q * (q - 1) / 2 + q * rem;
    };
    int pos = 0, cost = 0;
    for (int sz = int(counts.size()) - 1; sz >= 1; sz--) {
      cost += sz * (sumrank(pos + counts[sz]) - sumrank(pos));
      pos += counts[sz];
    }
    return cost;
  };
  int rankcost = rankproxy(hist);
  score += bias * rankcost;

  int bestscore = score;
  auto bestcl = cl;
  U bestcm = cm, besthm = hm, bestflip = flip;
  // CPU時間を設計に使い切らず、割り当てとオンライン応答の余裕を残す。
  int budget_ms = argc > 6 ? atoi(argv[6]) : 1000;
  for (int t = 0; t < steps; t++) {
    if (budget_ms > 0 && t % 2048 == 0 &&
        double(clock() - design_start) * 1000 / CLOCKS_PER_SEC >= budget_ms)
      break;
    double progress = double(t) / steps;
    if (t % 50 == 0) {
      int bitindex = content[rng() % bn];
      U bit = U(1) << bitindex;
      int old = totalcost();
      for (U &x : codes)
        x ^= bit;
      int delta = totalcost() - old;
      double temp = 128 * pow(0.3 / 8, progress);
      if (delta <= 0 || real() < exp(-delta / temp)) {
        flip ^= bit;
        score += delta;
      } else
        for (U &x : codes)
          x ^= bit;
    } else if (t % 25 == 0) {
      int xi = rng() % h, yi = rng() % bn, x = handles[xi], y = content[yi];
      U change = (U(1) << x) ^ (U(1) << y), nhm = hm ^ change;
      bool valid = true;
      for (auto &v : cl)
        if (!(common(v) & nhm)) {
          valid = false;
          break;
        }
      if (!valid)
        continue;
      int old = totalcost();
      cm ^= change;
      int delta = totalcost() - old;
      double temp = 128 * pow(0.3 / 8, progress);
      if (delta <= 0 || real() < exp(-delta / temp)) {
        hm = nhm;
        swap(handles[xi], content[yi]);
        score += delta;
      } else
        cm ^= change;
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
      auto next_hist = hist;
      next_hist[oldi.size()]--;
      next_hist[oldj.size()]--;
      next_hist[cl[i].size()]++;
      next_hist[cl[j].size()]++;
      int next_rank = rankproxy(next_hist);
      delta += bias * (next_rank - rankcost);
      double temp = 24 * pow(0.03 / 1.5, progress);
      if ((common(cl[i]) & hm) && (common(cl[j]) & hm) &&
          (delta <= 0 || real() < exp(-delta / temp))) {
        score += delta;
        hist = next_hist;
        rankcost = next_rank;
      } else {
        cl[i] = oldi;
        cl[j] = oldj;
      }
    }
    if (score < bestscore) {
      bestscore = score;
      bestcl = cl;
      bestcm = cm;
      besthm = hm;
      bestflip = flip;
    }
  }
  for (U &x : codes)
    x ^= flip ^ bestflip;
  flip = bestflip;
  cl = bestcl;
  cm = bestcm;
  hm = besthm;
  handles.clear();
  content.clear();
  for (int j = 0; j < n; j++)
    ((hm >> j & 1) ? handles : content).push_back(j);
  // 最初は白黒同数で割り当てる。後段で群サイズ・白黒枚数を自由にする。
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

  // 先頭色が各1/2と仮定し、先頭2枚異色の静的な重み付き順位を評価。
  auto slotcost = [&](int g) {
    vector<int> w[2];
    for (int col = 0; col < 2; col++) {
      for (int i : slots[g][col])
        w[col].push_back(cl[i].size());
      sort(w[col].rbegin(), w[col].rend());
    }
    int cost = 0;
    vector<int> rest;
    for (int col = 0; col < 2; col++)
      for (int z = 1; z < int(w[col].size()); z++)
        rest.push_back(w[col][z]);
    sort(rest.rbegin(), rest.rend());
    cost = w[0][0] + w[1][0];
    for (int z = 0; z < int(rest.size()); z++)
      cost += 2 * (z + 2) * rest[z];
    return cost;
  };
  vector<int> gcost(h);
  for (int g = 0; g < h; g++)
    gcost[g] = slotcost(g);
  int rounds = argc > 4 ? atoi(argv[4]) : 400000;
  for (int t = 0; t < rounds; t++) {
    int g = rng() % h, f = rng() % h, col = rng() % 2;
    if (g == f || slots[g][col].size() <= 1 ||
        slots[f][0].size() + slots[f][1].size() >= 24)
      continue;
    int ix = rng() % slots[g][col].size(), i = slots[g][col][ix];
    if (!(common(cl[i]) >> handles[f] & 1))
      continue;
    int nc = codes[cl[i][0]] >> handles[f] & 1;
    slots[g][col].erase(slots[g][col].begin() + ix);
    slots[f][nc].push_back(i);
    int cg = slotcost(g), cf = slotcost(f),
        delta = cg + cf - gcost[g] - gcost[f];
    double temp = 4 * pow(0.02 / 4, double(t) / rounds);
    if (delta <= 0 || real() < exp(-delta / temp)) {
      gcost[g] = cg;
      gcost[f] = cf;
    } else {
      slots[f][nc].pop_back();
      slots[g][col].insert(slots[g][col].begin() + ix, i);
    }
  }
  vector<vector<int>> layout(h);
  for (int g = 0; g < h; g++) {
    for (int col = 0; col < 2; col++)
      stable_sort(slots[g][col].begin(), slots[g][col].end(),
                  [&](int a, int b) { return cl[a].size() > cl[b].size(); });
    for (int col = 0; col < 2; col++)
      layout[g].push_back(slots[g][col][0]);
    vector<int> rest;
    for (int col = 0; col < 2; col++)
      for (int z = 1; z < int(slots[g][col].size()); z++)
        rest.push_back(slots[g][col][z]);
    stable_sort(rest.begin(), rest.end(),
                [&](int a, int b) { return cl[a].size() > cl[b].size(); });
    layout[g].insert(layout[g].end(), rest.begin(), rest.end());
  }

  vector<U> masks, blacks;
  for (int j : content) {
    masks.push_back(U(1) << j);
    blacks.push_back(U(1) << j);
  }
  vector<vector<int>> groups(h);
  vector<int> member(p), loc(k);
  for (int g = 0; g < h; g++)
    for (int i : layout[g]) {
      int item = masks.size();
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
          if (ix == 1 &&
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
    // 追加移動なしで先頭を対象、次を反対色、残りを重み順へ組み直す。
    int rank =
        find(groups[g].begin(), groups[g].end(), page) - groups[g].begin();
    int end = rank + 1;
    vector<int> desired{page}, rest;
    int partner = -1;
    for (int ix = 0; ix < end; ix++)
      if (groups[g][ix] != page) {
        int item = groups[g][ix];
        if (((blacks[item] ^ blacks[page]) >> handles[g] & 1) &&
            (partner < 0 || weight[item] > weight[partner]))
          partner = item;
      }
    if (partner >= 0)
      desired.push_back(partner);
    for (int ix = 0; ix < end; ix++)
      if (groups[g][ix] != page && groups[g][ix] != partner)
        rest.push_back(groups[g][ix]);
    stable_sort(rest.begin(), rest.end(),
                [&](int a, int b) { return weight[a] > weight[b]; });
    desired.insert(desired.end(), rest.begin(), rest.end());
    bool placed[192] = {};
    placed[page] = true;

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
