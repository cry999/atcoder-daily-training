// 商品ペアと取っ手に使う窓を同時に焼きなます。未来の注文は読まない。
// 設計・比較結果: ahc/ahc074/README.md
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <functional>
#include <iostream>
#include <numeric>
#include <random>
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
  int h = 14, steps = argc > 2 ? atoi(argv[2]) : 10000000;
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
  int score = 0;
  for (auto v : cl)
    if (v.size() == 2)
      score += distance(v[0], v[1]);
  int bestscore = score;
  auto bestcl = cl;
  U bestcm = cm, besthm = hm;
  // ペア交換だけでなく、取っ手と本体の窓も交換する。
  for (int t = 0; t < steps; t++) {
    double progress = double(t) / steps;
    if (t % 25 == 0) {
      int xi = rng() % h, yi = rng() % bn, x = handles[xi], y = content[yi];
      int delta = 0;
      U nhm = hm ^ (U(1) << x) ^ (U(1) << y);
      bool valid = true;
      for (auto &v : cl)
        if (v.size() == 2) {
          U diff = codes[v[0]] ^ codes[v[1]];
          delta += int(diff >> x & 1) - int(diff >> y & 1);
          if (!(~diff & nhm)) {
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
      if (cl[i].size() == 1)
        swap(i, j);
      if (cl[i].size() == 1)
        continue;
      int a = cl[i][0], b = cl[i][1], x = cl[j][0], y = -1,
          old = distance(a, b), nv;
      if (cl[j].size() == 2) {
        y = cl[j][1];
        if (rng() % 2)
          swap(x, y);
        old += distance(x, y);
        nv = distance(a, x) + distance(b, y);
      } else {
        if (rng() % 2)
          swap(a, b);
        nv = distance(a, x);
      }
      int delta = nv - old;
      double temp = 1.5 * pow(0.03 / 1.5, progress);
      if (delta <= 0 || real() < exp(-delta / temp)) {
        cl[i] = {a, x};
        cl[j] = y < 0 ? vector<int>{b} : vector<int>{b, y};
        score += delta;
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
  // 各取っ手の白黒を交互に並べ、必ず 1 操作で反転できるようにする。
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
  vector<int> order(k), tops(h);
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
    auto retire = [&](int group) {
      move(groups[group][tops[group]], k - 1);
      tops[group] = (tops[group] + 1) % groups[group].size();
    };
    if (current >= 0) {
      int oldg = loc[current];
      if ((oldg != g &&
           ((blacks[current] ^ target) >> handles[oldg] & 1) == 0) ||
          current == page)
        move(current, bn);
      else
        retire(oldg);
    }
    while (groups[g][tops[g]] != page)
      retire(g);
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
    int count = cut;
    for (int t = cut; t < bn; t++)
      if (patches >> content[bank[t]] & 1) {
        move(bank[t], 0);
        count++;
      }
    for (int t = 0; t < cut; t++)
      if (!(target >> content[bank[t]] & 1)) {
        move(bank[t], bn - 1);
        count--;
      }
    move(page, count);
    current = page;
    for (int group = 0; group < h; group++)
      if (group != g &&
          ((blacks[groups[group][tops[group]]] ^ target) >> handles[group] & 1))
        retire(group);
    cout << ans.size() << '\n';
    for (auto [x, d] : ans)
      cout << x << ' ' << d << '\n';
    cout.flush();
  }
}
