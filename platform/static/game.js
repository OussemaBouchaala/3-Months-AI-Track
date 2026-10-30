/* Bench: the game layer and the review system.
 *
 * - Player level: XP turns into a rank, from "Notebook Novice" to "AI Engineer".
 * - Unlocking: a level opens when the previous one is played (or its day has come).
 * - Celebrations: a level-cleared card, badges, level-ups and confetti (calm if the OS asks
 *   for reduced motion).
 * - Review: spaced repetition (Leitner boxes) over every flashcard and quiz question of the
 *   levels you've read. A card you remember comes back later and later; one you forget comes
 *   back tomorrow. Ten minutes a day keeps the early weeks fresh.
 * - Trophy room: rank, daily goal, streaks, activity heatmap, review boxes and badges.
 *
 * Loaded after index.html's main script, so it uses its globals (S, P, $, esc, inline, ...).
 */
const Game = (() => {
  const RANKS = ["Notebook Novice", "Tensor Tinkerer", "Prompt Apprentice", "Chunk Wrangler", "Retrieval Ranger",
    "Embedding Explorer", "Agent Handler", "Eval Engineer", "Pipeline Pilot", "RAG Architect", "Production Builder", "AI Engineer"];
  const DAILY_GOAL = 60;
  const NEW_PER_DAY = 12, SESSION_MAX = 20;
  const INTERVALS = [1, 1, 3, 7, 14, 30];          // days until the next review, by box (0 = forgotten)
  const MASTERED = 4;

  const addDays = (iso, n) => { const d = new Date(iso + "T12:00:00"); d.setDate(d.getDate() + n); return d.toISOString().slice(0, 10); };
  const reduceMotion = () => window.matchMedia?.("(prefers-reduced-motion: reduce)").matches || P().settings.calm;

  function init() {
    const p = P();
    p.review ??= {}; p.badges ??= {}; p.reviewLog ??= {}; p.xpLog ??= {}; p.reviewNew ??= {};
    p.examplesRun ??= 0;
    if (p.rank == null) p.rank = rankOf(xp()).n;
    const known = new Set(Object.keys(p.badges));
    for (const b of BADGES) if (!known.has(b.id) && safe(b.test)) p.badges[b.id] = "before";   // no fireworks for old wins
  }
  const safe = f => { try { return !!f(); } catch { return false; } };

  /* ---------- XP, ranks, daily goal ---------- */
  function bonusXP() {
    const p = P();
    const reviews = Object.values(p.reviewLog).reduce((a, b) => a + b, 0);
    const badges = Object.keys(p.badges || {}).length;
    return reviews * 2 + badges * 25 + Math.min(p.examplesRun || 0, 300);
  }
  function rankOf(x) {
    const n = Math.min(RANKS.length - 1, Math.floor(Math.sqrt(x / 120)));
    const lo = 120 * n * n, hi = 120 * (n + 1) * (n + 1);
    return { n, title: RANKS[n], lo, hi, pct: n === RANKS.length - 1 ? 100 : Math.round(100 * (x - lo) / (hi - lo)) };
  }
  function xpToday() {
    const p = P(), t = todayISO();
    p.xpDay ??= { date: t, start: xp() };
    if (p.xpDay.date !== t) p.xpDay = { date: t, start: xp() };
    const today = Math.max(0, xp() - p.xpDay.start);
    p.xpLog[t] = today;
    return today;
  }

  /* ---------- Unlocking ---------- */
  function played(d) {
    return dayDone(d) || (!!P().lessons[d.id] && (!d.quiz?.length || !!P().quiz[d.id]));
  }
  function isLocked(d) {
    const days = allDays(), i = days.indexOf(d);
    return i > 0 && !played(days[i - 1]) && d.date > todayISO();
  }
  function tryOpen(id) {
    const d = findDay(id);
    if (d && isLocked(d)) {
      const prev = allDays()[allDays().indexOf(d) - 1];
      return toast(`🔒 Locked. Play "${prev.title}" first (lesson + quiz), or wait for ${d.weekday} ${d.date.slice(5).replace("-", "/")}.`);
    }
    selectDay(id);
  }

  /* ---------- Badges ---------- */
  const count = o => Object.values(o || {}).filter(Boolean).length;
  const labsPassed = () => Object.values(P().checks).filter(c => c.passed === c.total).length;
  const threeStars = () => allDays().filter(d => stars(d).every(Boolean)).length;
  const reviewsDone = () => Object.values(P().reviewLog).reduce((a, b) => a + b, 0);
  const mastered = () => Object.values(P().review).filter(r => r.box >= MASTERED).length;
  const bestStreak = () => {
    const days = [...new Set(P().activity)].sort(); let best = 0, run = 0, prev = null;
    for (const d of days) { run = prev && addDays(prev, 1) === d ? run + 1 : 1; best = Math.max(best, run); prev = d; }
    return best;
  };
  const arenaCleared = n => { const w = S.weeks.find(w => w.n === n); return !!w?.days.length && w.days.every(dayDone); };
  const bossBeaten = n => S.weeks.find(w => w.n === n)?.days.some(d => (P().retest[d.id]?.best || 0) >= 8);

  const BADGES = [
    { id: "first-light", icon: "💡", name: "First Light", desc: "Read your first lesson", test: () => count(P().lessons) >= 1 },
    { id: "bookworm", icon: "📚", name: "Bookworm", desc: "Read 25 lessons", test: () => count(P().lessons) >= 25 },
    { id: "green-check", icon: "✅", name: "Green Check", desc: "Pass your first lab", test: () => labsPassed() >= 1 },
    { id: "bug-squasher", icon: "🪲", name: "Bug Squasher", desc: "Pass 20 labs", test: () => labsPassed() >= 20 },
    { id: "flawless", icon: "🎯", name: "Flawless", desc: "Score 100% on a quiz", test: () => Object.values(P().quiz).some(q => q.best === q.total) },
    { id: "three-star", icon: "⭐", name: "Three-Star General", desc: "Earn 3 stars on 10 levels", test: () => threeStars() >= 10 },
    { id: "boss-slayer", icon: "🐉", name: "Boss Slayer", desc: "Beat a Sunday boss", test: () => Object.values(P().retest).some(r => r.best >= 8) },
    { id: "on-fire", icon: "🔥", name: "On Fire", desc: "A 3-day streak", test: () => bestStreak() >= 3 },
    { id: "unstoppable", icon: "⚡", name: "Unstoppable", desc: "A 7-day streak", test: () => bestStreak() >= 7 },
    { id: "marathon", icon: "🏃", name: "Marathon", desc: "A 21-day streak", test: () => bestStreak() >= 21 },
    { id: "scribe", icon: "✍️", name: "Scribe", desc: "Write notes for 5 levels", test: () => Object.values(P().notes).filter(n => n >= 40).length >= 5 },
    { id: "first-recall", icon: "🧠", name: "First Recall", desc: "Finish a review session", test: () => reviewsDone() >= 5 },
    { id: "long-memory", icon: "🗄️", name: "Long-Term Memory", desc: "Review 100 cards", test: () => reviewsDone() >= 100 },
    { id: "iron-memory", icon: "🛡️", name: "Iron Memory", desc: "Master 25 cards (box 4+)", test: () => mastered() >= 25 },
    { id: "explorer", icon: "🔭", name: "Code Explorer", desc: "Run 25 walkthrough examples", test: () => (P().examplesRun || 0) >= 25 },
    { id: "goal-getter", icon: "🎖️", name: "Goal Getter", desc: `Reach the daily goal (${DAILY_GOAL} XP)`, test: () => Object.values(P().xpLog).some(x => x >= DAILY_GOAL) },
    ...Array.from({ length: 12 }, (_, i) => ({
      id: `arena-${i + 1}`, icon: "🏆", arena: i + 1, name: `Arena ${i + 1} Champion`,
      desc: `Clear every level of arena ${i + 1}, or beat its boss`, test: () => arenaCleared(i + 1) || bossBeaten(i + 1),
    })),
    { id: "phase-1", icon: "🥉", name: "Phase 1 Complete", desc: "Champion of arenas 1-6", test: () => [1, 2, 3, 4, 5, 6].every(n => arenaCleared(n) || bossBeaten(n)) },
    { id: "phase-2", icon: "🥇", name: "AI Engineer", desc: "Champion of all 12 arenas", test: () => S.weeks.every(w => arenaCleared(w.n) || bossBeaten(w.n)) },
  ];

  /* Runs after every progress change: new badges and rank-ups get a toast and confetti, staggered. */
  let pending = false;
  function check() {
    if (pending || !S.weeks.length) return;
    pending = true;
    setTimeout(() => {
      pending = false;
      const p = P(), fresh = [];
      for (const b of BADGES) if (!p.badges[b.id] && safe(b.test)) { p.badges[b.id] = todayISO(); fresh.push(b); }
      const days = allDays(), seen = new Set(p.playedSeen ||= days.filter(played).map(d => d.id));
      const unlockedNow = days.filter(d => !seen.has(d.id) && played(d)).map(d => days[days.indexOf(d) + 1])
        .filter(n => n && n.date > todayISO());
      for (const d of days) if (!seen.has(d.id) && played(d)) p.playedSeen.push(d.id);
      const r = rankOf(xp());
      const rankUp = r.n > (p.rank ?? 0);
      if (rankUp) p.rank = r.n;
      xpToday();
      if (fresh.length || rankUp) { saveProgress(); renderHeader(); }
      let delay = 300;
      if (unlockedNow.length) {
        const n = unlockedNow.at(-1); S.unlocked = n.id; saveProgress(); renderHeader();
        setTimeout(() => toast(`🔓 Level unlocked: ${n.title}`), delay); delay += 2600;
      }
      if (rankUp) { setTimeout(() => { toast(`⬆️ Rank up! You are now a ${r.title}`); confetti(); }, delay); delay += 2600; }
      for (const b of fresh) { setTimeout(() => { toast(`${b.icon} Badge unlocked: ${b.name}`); confetti(70); }, delay); delay += 2600; }
    }, 600);
  }

  /* ---------- Header chips ---------- */
  function headerHTML() {
    const x = xp(), r = rankOf(x), due = dueCount();
    return `<button class="g-rank" data-g="trophies" title="Your rank and trophy room: ${r.lo}-${r.hi} XP for this rank">
        <b>${esc(r.title)}</b><span class="g-bar"><span style="width:${r.pct}%"></span></span><small>${x} XP · rank ${r.n + 1}</small></button>
      <button class="g-review ${due ? "due" : ""}" data-g="review" title="Spaced-repetition review of the levels you've read">
        🧠 Review${due ? `<span class="g-count">${due}</span>` : ""}</button>`;
  }
  function bindHeader(el) {
    el.addEventListener("click", e => {
      const b = e.target.closest("[data-g]"); if (!b) return;
      if (b.dataset.g === "review") openReview();
      if (b.dataset.g === "trophies") openTrophies();
    });
  }

  /* ---------- Review deck (Leitner boxes) ---------- */
  function deck(filterWeek) {
    const cards = [];
    for (const d of allDays()) {
      if (!P().lessons[d.id]) continue;
      if (filterWeek != null && weekOfDay(d.id) !== filterWeek) continue;
      const re = /^:::cards[^\n]*\n([\s\S]*?)^:::[ \t]*$/gm; let m, i = 0;
      while ((m = re.exec(d.lesson || ""))) {
        for (const line of m[1].split("\n").filter(l => l.includes("::"))) {
          const [front, back] = line.split("::").map(x => x.trim());
          cards.push({ id: `${d.id}:c${i++}`, kind: "flash", front, back, day: d });
        }
      }
      (d.quiz || []).forEach((q, j) => cards.push({ id: `${d.id}:q${j}`, kind: "quiz", q, day: d }));
    }
    return cards;
  }
  function dueCards(filterWeek) {
    const t = todayISO(), st = P().review;
    const all = deck(filterWeek);
    const due = all.filter(c => st[c.id] && st[c.id].due <= t).sort((a, b) => st[a.id].due.localeCompare(st[b.id].due));
    const newLeft = filterWeek != null ? SESSION_MAX : Math.max(0, NEW_PER_DAY - (P().reviewNew[t] || 0));
    const fresh = all.filter(c => !st[c.id]).slice(0, newLeft);
    return [...due, ...fresh];
  }
  const dueCount = () => S.weeks.length ? Math.min(SESSION_MAX, dueCards().length) : 0;

  function grade(card, remembered) {
    const p = P(), t = todayISO();
    const prev = p.review[card.id];
    if (!prev) p.reviewNew[t] = (p.reviewNew[t] || 0) + 1;
    const box = remembered ? Math.min(INTERVALS.length - 1, (prev?.box || 0) + 1) : 0;
    p.review[card.id] = { box, due: addDays(t, INTERVALS[box]), seen: (prev?.seen || 0) + 1, last: t };
    p.reviewLog[t] = (p.reviewLog[t] || 0) + 1;
    logActivity(); saveProgress();
  }

  function openReview(filterWeek) {
    const cards = shuffle(dueCards(filterWeek)).slice(0, SESSION_MAX);
    const title = filterWeek != null ? `Arena ${S.weeks[filterWeek].n} recap` : "Daily review";
    const ses = { cards, i: 0, ok: 0, again: [], revealed: false, choice: null, xp0: xp() };
    const ov = $("#overlay");
    if (!cards.length) {
      const total = deck().length;
      ov.innerHTML = `<div class="scrim" data-close></div><section class="g-modal" role="dialog" aria-label="${title}">
        <div class="g-modal-body center"><div class="g-big">🧠</div><h2>Nothing to review right now</h2>
        <p class="empty">${total ? `All ${total} cards from the lessons you've read are scheduled for later days. Come back tomorrow.`
          : "Cards join your deck when you read a lesson: its flashcards and its quiz questions."}</p>
        <button class="btn go" data-close>Back to Bench</button></div></section>`;
      return bindOverlayClose();
    }
    const render = () => {
      if (ses.i >= ses.cards.length) return finish();
      const c = ses.cards[ses.i], box = P().review[c.id]?.box;
      const meta = `<div class="g-card-meta"><span>${esc(c.day.title)}</span><span>${box == null ? "new card" : `box ${box}`}</span></div>`;
      let body;
      if (c.kind === "flash") {
        body = `<div class="g-card"><p class="g-front">${inline(c.front)}</p>
          ${ses.revealed ? `<div class="g-back">${inline(c.back)}</div>` : `<p class="hint">Say the answer in your head, then reveal it.</p>`}</div>
          <div class="g-actions">${ses.revealed
            ? `<button class="btn" data-r="again">✗ Forgot it</button><button class="btn go" data-r="good">✓ Remembered</button>`
            : `<button class="btn primary" data-r="show">Show answer</button>`}</div>`;
      } else {
        const q = c.q; ses.order ??= shuffle(q.options.map((_, j) => j));
        body = `<div class="g-card"><p class="g-front">${inline(q.q.split("\n")[0])}</p>${q.q.includes("\n") ? `<pre>${esc(q.q.split("\n").slice(1).join("\n"))}</pre>` : ""}
          ${ses.order.map(j => `<button class="g-opt ${ses.choice == null ? "" : j === q.answer ? "right" : j === ses.choice ? "wrong" : ""}" data-opt="${j}" ${ses.choice != null ? "disabled" : ""}>${inline(q.options[j])}</button>`).join("")}
          ${ses.choice != null ? `<div class="g-back">${inline(q.explain || "")}</div>` : ""}</div>
          <div class="g-actions">${ses.choice != null ? `<button class="btn go" data-r="next">Next →</button>` : ""}</div>`;
      }
      ov.innerHTML = `<div class="scrim" data-close></div><section class="g-modal" role="dialog" aria-label="${title}">
        <div class="drawer-head"><div><h2>${title}</h2><p>Card ${ses.i + 1} of ${ses.cards.length} · ${ses.ok} remembered</p></div>
        <button class="btn" data-close>Stop</button></div>
        <div class="g-progress"><span style="width:${Math.round(100 * ses.i / ses.cards.length)}%"></span></div>
        <div class="g-modal-body">${meta}${body}</div></section>`;
    };
    const next = remembered => {
      const c = ses.cards[ses.i];
      grade(c, remembered);
      if (remembered) ses.ok++;
      else if (!ses.again.includes(c.id)) { ses.again.push(c.id); ses.cards.push(c); }   // one more try at the end
      ses.i++; ses.revealed = false; ses.choice = null; ses.order = null; render();
    };
    const finish = () => {
      const gained = xp() - ses.xp0;
      ov.innerHTML = `<div class="scrim" data-close></div><section class="g-modal" role="dialog" aria-label="${title} done">
        <div class="g-modal-body center"><div class="g-big">🎉</div><h2>${title} done</h2>
        <p><b>${ses.ok}</b> of ${ses.cards.length} remembered · <b>+${gained} XP</b></p>
        <p class="empty">Remembered cards come back in ${INTERVALS.slice(1, 5).join(", ")} days as they climb the boxes. Forgotten ones come back tomorrow.</p>
        <button class="btn go" data-close>Back to Bench</button></div></section>`;
      confetti(); renderHeader(); check();
    };
    ov.onclick = e => {
      if (e.target.closest("[data-close]")) { closeOverlay(); renderHeader(); return; }
      const r = e.target.closest("[data-r]")?.dataset.r, opt = e.target.closest("[data-opt]");
      if (r === "show") { ses.revealed = true; render(); }
      if (r === "good") next(true);
      if (r === "again") next(false);
      if (r === "next") next(ses.choice === ses.cards[ses.i].q.answer);
      if (opt && ses.choice == null) { ses.choice = +opt.dataset.opt; render(); }
    };
    render();
  }

  /* ---------- Level cleared ---------- */
  function levelCleared(d) {
    const days = allDays(), next = days[days.indexOf(d) + 1], st = stars(d);
    const w = S.weeks[weekOfDay(d.id)], last = w.days.at(-1) === d;
    S.unlocked = next?.id;
    $("#overlay").innerHTML = `<div class="scrim" data-close></div><section class="g-modal" role="dialog" aria-label="Level cleared">
      <div class="g-modal-body center">
        <p class="kicker">Arena ${w.n} · ${esc(w.title)}</p><h2>Level cleared!</h2><p class="g-level-name">${esc(d.title)}</p>
        <div class="g-stars">${st.map((s, i) => `<span class="${s ? "on" : ""}" style="animation-delay:${0.25 + i * 0.3}s">★</span>`).join("")}</div>
        <p class="empty">★ lesson read · ★ every lab passing · ★ perfect quiz</p>
        ${next ? `<div class="g-unlock"><span class="g-lock">🔓</span><div><small>${last ? `Arena ${S.weeks[weekOfDay(next.id)].n} unlocked` : "Next level unlocked"}</small><b>${esc(next.title)}</b></div></div>` : `<p><b>You finished the whole plan.</b></p>`}
        <div class="g-actions center"><button class="btn" data-g="map">Open the map</button>${next ? `<button class="btn go" data-g="next">Play next level →</button>` : ""}</div>
      </div></section>`;
    $("#overlay").onclick = e => {
      if (e.target.closest("[data-close]")) return closeOverlay();
      const g = e.target.closest("[data-g]")?.dataset.g;
      if (g === "map") openMap();
      if (g === "next") { closeOverlay(); selectDay(next.id, "learn"); }
    };
    confetti(160);
    check();
  }

  /* ---------- Trophy room ---------- */
  function openTrophies() {
    const x = xp(), r = rankOf(x), today = xpToday(), p = P();
    const goal = Math.min(100, Math.round(100 * today / DAILY_GOAL));
    const boxes = [0, 0, 0, 0, 0, 0]; for (const v of Object.values(p.review)) boxes[v.box]++;
    const total = deck().length, unseen = total - Object.keys(p.review).length;
    const weak = deck().filter(c => p.review[c.id] && p.review[c.id].box === 0 && p.review[c.id].seen > 1).slice(0, 5);
    // 12 weeks of activity, Monday first.
    const start = new Date(); start.setDate(start.getDate() - 83 - ((start.getDay() + 6) % 7));
    const cells = Array.from({ length: 84 + ((new Date().getDay() + 6) % 7) + 1 }, (_, i) => {
      const iso = addDays(start.toISOString().slice(0, 10), i), v = p.xpLog[iso] || (p.activity.includes(iso) ? 10 : 0);
      const lvl = v === 0 ? 0 : v < 20 ? 1 : v < 45 ? 2 : v < 80 ? 3 : 4;
      return `<span class="g-cell l${lvl}" title="${iso}: ${v ? v + " XP" : "no activity"}"></span>`;
    }).join("");
    const earned = BADGES.filter(b => p.badges[b.id]).length;
    $("#overlay").innerHTML = `<div class="scrim" data-close></div><section class="map g-trophies" role="dialog" aria-label="Trophy room">
      <div class="drawer-head"><div><h2>Trophy room</h2><p>Your rank, your habits and everything you've unlocked.</p></div><button class="btn" data-close>Close</button></div>
      <div class="map-body g-tro-body">
        <div class="arena g-player"><small>Rank ${r.n + 1} of ${RANKS.length}</small><h3>${esc(r.title)}</h3>
          <div class="g-bar big"><span style="width:${r.pct}%"></span></div>
          <div class="meta">${x} XP · ${r.n === RANKS.length - 1 ? "top rank" : `${r.hi - x} XP to ${esc(RANKS[r.n + 1])}`}</div>
          <div class="g-ranks">${RANKS.map((t, i) => `<span class="${i <= r.n ? "on" : ""}" title="${120 * i * i} XP">${esc(t)}</span>`).join("")}</div></div>
        <div class="arena g-today"><small>Today</small>
          <div class="g-ring" style="--p:${goal}"><div><b>${today}</b><span>/ ${DAILY_GOAL} XP</span></div></div>
          <div class="g-kv"><div><b>${streak()}</b>day streak</div><div><b>${bestStreak()}</b>best streak</div><div><b>${dueCount()}</b>cards due</div></div>
          <button class="btn go small" data-g="review">🧠 Start today's review</button></div>
        <div class="arena g-wide"><small>Last 12 weeks</small><div class="g-heat">${cells}</div>
          <div class="g-legend">less <span class="g-cell l0"></span><span class="g-cell l1"></span><span class="g-cell l2"></span><span class="g-cell l3"></span><span class="g-cell l4"></span> more</div></div>
        <div class="arena g-wide"><small>Memory · Leitner boxes</small>
          <div class="g-boxes">${boxes.map((n, i) => `<div><b>${n}</b><span>${i === 0 ? "forgot" : `box ${i}`}</span><em>${i === 0 ? "tomorrow" : `every ${INTERVALS[i]} d`}</em></div>`).join("")}
            <div class="unseen"><b>${unseen}</b><span>new</span><em>${NEW_PER_DAY}/day</em></div></div>
          ${weak.length ? `<p class="meta"><b>Weak spots:</b> ${weak.map(c => `${esc(c.kind === "flash" ? c.front : c.q.q.split("\n")[0])} <i>(${esc(c.day.title)})</i>`).join(" · ")}</p>` : ""}</div>
        <div class="arena g-wide"><small>Badges · ${earned} of ${BADGES.length}</small>
          <div class="g-badges">${BADGES.map(b => `<div class="g-badge ${p.badges[b.id] ? "on" : ""}" title="${esc(b.desc)}${p.badges[b.id] && p.badges[b.id] !== "before" ? " · " + p.badges[b.id] : ""}">
            <span class="g-medal">${b.icon}</span><b>${esc(b.name)}</b><span>${esc(b.desc)}</span></div>`).join("")}</div></div>
      </div></section>`;
    $("#overlay").onclick = e => {
      if (e.target.closest("[data-close]")) return closeOverlay();
      if (e.target.closest("[data-g=review]")) openReview();
    };
  }

  /* ---------- Map extras ---------- */
  function arenaExtras(w, i) {
    const champ = P().badges[`arena-${w.n}`];
    const read = w.days.some(d => P().lessons[d.id]);
    return `<div class="g-arena-foot">${champ ? `<span class="g-champ" title="Arena ${w.n} Champion">🏆 Champion</span>` : ""}
      ${read ? `<button class="btn small" data-recap="${i}" title="Review this arena's flashcards and quiz questions">🧠 Recap</button>` : ""}</div>`;
  }

  /* ---------- Confetti: 140 squares, gravity, gone in 2 seconds ---------- */
  function confetti(n = 140) {
    if (reduceMotion()) return;
    const c = document.createElement("canvas"); c.className = "g-confetti";
    c.width = innerWidth; c.height = innerHeight; document.body.appendChild(c);
    const ctx = c.getContext("2d"), colors = ["#2650E0", "#E8A317", "#1E8556", "#FFE066", "#7A5AF8"];
    const ps = Array.from({ length: n }, () => ({ x: innerWidth / 2 + (Math.random() - .5) * 200, y: innerHeight / 3,
      vx: (Math.random() - .5) * 16, vy: Math.random() * -14 - 4, s: 5 + Math.random() * 5, r: Math.random() * 6, c: colors[Math.random() * 5 | 0] }));
    let f = 0;
    (function tick() {
      ctx.clearRect(0, 0, c.width, c.height);
      for (const p of ps) { p.vy += .35; p.x += p.vx; p.y += p.vy; p.r += .1; ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.r); ctx.fillStyle = p.c; ctx.fillRect(-p.s / 2, -p.s / 2, p.s, p.s * .6); ctx.restore(); }
      if (++f < 120) requestAnimationFrame(tick); else c.remove();
    })();
  }

  return { init, check, headerHTML, bindHeader, isLocked, tryOpen, levelCleared, openReview, openTrophies,
    arenaExtras, bonusXP, xpToday, confetti, rankOf, deck, BADGES };
})();
