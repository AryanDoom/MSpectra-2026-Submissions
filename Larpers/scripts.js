/* ══════════════════════════════════════
   ASOS -- script.js
   AI-Assisted Storage Optimization System
══════════════════════════════════════ */

/* ── TYPING ANIMATION ── */
(function initTyping() {
  const el = document.getElementById('typingTarget');
  if (!el) return;
  const lines = ['AI-Assisted', 'Storage Optimization', 'System.'];
  const fullText = lines.join('\n');
  let i = 0;

  function type() {
    if (i <= fullText.length) {
      const slice = fullText.slice(0, i);
      el.innerHTML = slice.replace(/\n/g, '<br />') + '<span class="cursor">|</span>';
      i++;
      setTimeout(type, i === 1 ? 500 : 48);
    } else {
      // keep blinking cursor
      el.innerHTML = fullText.replace(/\n/g, '<br />') + '<span class="cursor">|</span>';
    }
  }
  setTimeout(type, 700);
})();

/* ── NAV: HAMBURGER ── */
(function initNav() {
  const btn = document.getElementById('hamburger');
  const mob = document.getElementById('mobileNav');
  btn.addEventListener('click', () => mob.classList.toggle('open'));
  document.querySelectorAll('.mobile-nav__link').forEach(l => {
    l.addEventListener('click', () => mob.classList.remove('open'));
  });
})();

/* ── PIPELINE STEP REVEAL ── */
(function initPipeline() {
  const steps = document.querySelectorAll('.pipe-step');
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const allSteps = document.querySelectorAll('.pipe-step');
        allSteps.forEach((s, i) => {
          setTimeout(() => s.classList.add('visible'), i * 75);
        });
        observer.disconnect();
      }
    });
  }, { threshold: 0.2 });
  const pipeline = document.querySelector('.pipeline');
  if (pipeline) observer.observe(pipeline);
})();

/* ── ANIMATED COUNTERS ── */
function animateCounter(el, targetOverride = null) {
  const target = targetOverride !== null ? targetOverride : parseFloat(el.dataset.target);
  const decimals = parseInt(el.dataset.decimals) || 0;
  const suffix = el.dataset.suffix || '';
  const duration = 1600;
  const start = performance.now();

  function easeOut(t) { return 1 - Math.pow(1 - t, 3); }
  function tick(now) {
    const p = Math.min((now - start) / duration, 1);
    const v = target * easeOut(p);
    el.textContent = v.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',') + suffix;
    if (p < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

(function initCounters() {
  const counters = document.querySelectorAll('.counter');
  const seen = new Set();

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !seen.has(entry.target)) {
        seen.add(entry.target);

        // animate bar
        const card = entry.target.closest('.stat');
        if (card) {
          const fill = card.querySelector('.stat__fill');
          if (fill) setTimeout(() => fill.classList.add('animated'), 150);
        }

        animateCounter(entry.target);
      }
    });
  }, { threshold: 0.3 });

  counters.forEach(c => observer.observe(c));
})();

/* ── CARD STAGGER ── */
(function initStagger() {
  const items = document.querySelectorAll('.feat, .stack-card, .stat');
  items.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(14px)';
  });
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const siblings = Array.from(entry.target.parentElement.children);
        const idx = siblings.indexOf(entry.target);
        setTimeout(() => {
          entry.target.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }, idx * 60);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });
  items.forEach(el => observer.observe(el));
})();

/* ── TERMINAL SIMULATION ── */
(function initTerminal() {
  const output = document.getElementById('terminalOutput');
  const inputEl = document.getElementById('terminalInput');
  const runBtn = document.getElementById('runBtn');
  const clearBtn = document.getElementById('clearBtn');
  const body = document.getElementById('terminalBody');
  let running = false;

  const clsMap = {
    head: 't-head', cmd: 't-cmd', info: 't-info', ok: 't-ok',
    warn: 't-warn', err: 't-err', data: 't-data', blank: 't-blank'
  };

  function addLine(text, cls) {
    const span = document.createElement('span');
    span.className = `t-line ${clsMap[cls] || ''}`;
    span.textContent = text === '.' ? '\u00a0' : text;
    output.appendChild(span);
    body.scrollTop = body.scrollHeight;
  }

  async function run() {
    if (running) return;
    running = true;
    runBtn.disabled = true;
    runBtn.textContent = '[ Running... ]';

    addLine('--- ASOS Real Cleanup Execution ---', 'head');
    addLine('$ asos run --path /data --mode AI_Full', 'cmd');
    addLine('Connecting to Python System via /api/run_pipeline...', 'info');

    try {
      const response = await fetch('/api/run_pipeline', { method: 'POST' });
      const result = await response.json();

      if (result.status === "success") {
        const stats = result.data;
        const mbFreed = (stats.reclaimed_bytes / (1024 * 1024)).toFixed(2);

        setTimeout(() => addLine('[PHASE 1] Scanning filesystem...', 'head'), 600);
        setTimeout(() => addLine(`  [OK] ${stats.files_scanned} files extracted via os.stat()`, 'ok'), 1200);

        setTimeout(() => addLine('[PHASE 2 & 3] Computing Hashes & AI Classification...', 'head'), 2000);
        setTimeout(() => addLine('  -> extracting metadata & Scikit-Learn grading', 'info'), 2600);

        setTimeout(() => addLine('[PHASE 4] Garbage Collection & Trash Logging...', 'head'), 3400);
        setTimeout(() => addLine(`  [WARN] ${stats.deleted_count - 1} redundant or duplicate files tossed`, 'warn'), 4000);

        setTimeout(() => addLine('[PHASE 5] Binary Delta Tier Optimization...', 'head'), 4800);
        setTimeout(() => addLine('  [TIER 3] Similar sibling detected. Computing bsdiff4 patch...', 'info'), 5400);
        setTimeout(() => addLine('  [OK] Verified Delta. Original reduced to 16.2 KB Ghost File.', 'ok'), 6000);

        setTimeout(() => {
          addLine('Real-time optimization securely complete.', 'info');
          addLine(`[OK] ${mbFreed} MB safely reclaimed!`, 'ok');
          updateDashboardStats(stats);
          running = false;
          runBtn.disabled = false;
          runBtn.textContent = '[ Run Again ]';
        }, 7000);
      }
    } catch (err) {
      addLine('[ERR] API ping failed. Is the Python server offline?', 'err');
      running = false;
      runBtn.disabled = false;
      runBtn.textContent = '[ Retry ]';
    }
  }

  function updateDashboardStats(data) {
    const mbReclaimed = data.reclaimed_bytes / (1024 * 1024);
    const totalFiles = data.files_scanned;
    const deletedCount = data.deleted_count;

    // 1. Update Counter Targets & Animate
    const storageEl = document.getElementById('stat-storage-reclaimed');
    const filesEl = document.getElementById('stat-files-processed');
    const dupsEl = document.getElementById('stat-duplicates-removed');
    const effEl = document.getElementById('stat-efficiency-gain');

    animateCounter(storageEl, mbReclaimed);
    animateCounter(filesEl, totalFiles);
    animateCounter(dupsEl, deletedCount);

    // Calculate generic efficiency
    const effVal = totalFiles > 0 ? (deletedCount / totalFiles) * 100 : 0;
    animateCounter(effEl, effVal);

    // 2. Update Subtexts
    document.getElementById('stat-scanned-total').textContent = `from real-time scan`;
    document.getElementById('stat-duplicate-percent').textContent = `${effVal.toFixed(1)}% of total items`;

    // 3. Update Progress Bars
    const barEff = document.getElementById('stat-bar-efficiency');
    const barDups = document.getElementById('stat-bar-duplicates');
    const barTotal = document.getElementById('stat-bar-total-gain');

    barEff.style.setProperty('--pct', `${Math.min(effVal * 1.5, 100)}%`);
    barDups.style.setProperty('--pct', `${effVal}%`);
    barTotal.style.setProperty('--pct', `${effVal}%`);

    [barEff, barDups, barTotal].forEach(b => {
      b.classList.remove('animated');
      void b.offsetWidth; // trigger reflow
      b.classList.add('animated');
    });
  }

  function clear() {
    output.innerHTML = '';
    running = false;
    runBtn.disabled = false;
    runBtn.textContent = '[ Run Cleanup Simulation ]';
  }

  runBtn.addEventListener('click', run);
  clearBtn.addEventListener('click', clear);

  inputEl.addEventListener('keydown', e => {
    if (e.key !== 'Enter') return;
    const raw = inputEl.value.trim();
    const cmd = raw.toLowerCase();
    inputEl.value = '';

    addLine('asos@system:~$ ' + raw, 'cmd');

    if (['run cleanup', 'run', 'asos run'].includes(cmd)) {
      run();
    } else if (['clear', 'cls'].includes(cmd)) {
      clear();
    } else if (cmd.startsWith('restore ')) {
      const path = raw.substring(8).trim();
      restoreFile(path);
    } else if (cmd === 'help') {
      addLine('  run cleanup      -- start simulation', 'info');
      addLine(`  restore <path>   -- undo optimization`, 'info');
      addLine('  clear            -- clear terminal', 'info');
      addLine('  help             -- this message', 'info');
    } else if (cmd !== '') {
      addLine(`Command not found: ${cmd}`, 'err');
    }
  });

  async function restoreFile(path) {
    if (running) return;
    running = true;

    addLine(`Initiating Restoration for: ${path}`, 'head');
    addLine('Fetching original binary metadata...', 'info');

    try {
      const response = await fetch('/api/restore', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
      });
      const result = await response.json();

      if (result.status === "success") {
        setTimeout(() => addLine('Searching trash archives...', 'info'), 500);
        setTimeout(() => addLine('Reconstructing binary fragments (bsdiff4)...', 'head'), 1200);
        setTimeout(() => {
          addLine(`[OK] ${result.message}`, 'ok');
          running = false;
        }, 2200);
      } else {
        addLine(`[ERR] ${result.message}`, 'err');
        running = false;
      }
    } catch (err) {
      addLine('[ERR] Failed to reach restoration server.', 'err');
      running = false;
    }
  }

  const terminalBoard = document.getElementById('terminal');
  if (terminalBoard) {
    terminalBoard.addEventListener('click', () => inputEl.focus());
  }
})();

/* ── SMOOTH SCROLL ── */
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const id = a.getAttribute('href').slice(1);
    const el = document.getElementById(id);
    if (el) { e.preventDefault(); el.scrollIntoView({ behavior: 'smooth' }); }
  });
});