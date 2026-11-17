(function () {
  'use strict';

  // ---------------------------------------------------------------- utils ---
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  function lite(s) {
    return esc(s)
      .replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/^[-*]\s+/gm, '· ')
      .replace(/\n/g, '<br>');
  }

  var LEC_LABEL = {
    lec01: 'L1', lec01s: 'L1补', lec02: 'L2', lec03: 'L3', lec04: 'L4', lec05: 'L5',
    lec06: 'L6', lec07: 'L7', lec08: 'L8A', lec08b: 'L8B', lec08s: 'L8C',
    lec09: 'L9', lec10: 'L10', lec12: 'L12'
  };

  // ------------------------------------------------------------- lightbox ---
  var lb = $('#lightbox'), lbimg = $('#lbimg');
  if (lb) {
    document.addEventListener('click', function (e) {
      var img = e.target.closest && e.target.closest('.shot img');
      if (img) { lbimg.src = img.src; lb.classList.add('on'); e.preventDefault(); }
      else if (e.target === lb || e.target === lbimg) { lb.classList.remove('on'); }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') lb.classList.remove('on');
    });
  }

  // ------------------------------------------------------------ TOC filter ---
  var f = $('#filter');
  if (f) {
    f.addEventListener('input', function () {
      var q = f.value.trim().toLowerCase();
      $$('.toc a').forEach(function (a) {
        a.style.display = (!q || a.textContent.toLowerCase().indexOf(q) >= 0) ? '' : 'none';
      });
    });
  }

  // ------------------------------------------- active TOC + keyboard nav ---
  var slides = $$('.slide');
  var current = null;
  if (slides.length) {
    var links = {};
    $$('.toc a').forEach(function (a) { links[a.getAttribute('data-n')] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          var n = en.target.getAttribute('data-n');
          if (current && links[current]) links[current].classList.remove('active');
          current = n;
          if (links[n]) {
            links[n].classList.add('active');
            var side = $('.side-inner');
            if (side && window.innerWidth > 1000) {
              var r = links[n].getBoundingClientRect(), sr = side.getBoundingClientRect();
              if (r.top < sr.top + 40 || r.bottom > sr.bottom - 40) side.scrollTop += r.top - sr.top - 120;
            }
          }
        }
      });
    }, { rootMargin: '-15% 0px -70% 0px' });
    slides.forEach(function (s) { io.observe(s); });

    document.addEventListener('keydown', function (e) {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft' && e.key !== 'j' && e.key !== 'k') return;
      var cur = current ? parseInt(current, 10) : 1;
      var next = (e.key === 'ArrowRight' || e.key === 'j') ? cur + 1 : cur - 1;
      var target = document.getElementById('s' + next);
      if (target) target.scrollIntoView({ block: 'start' });
      e.preventDefault();
    });
  }

  // ------------------------------------------------------- term popover ---
  var G = window.GLOSSARY || {};
  var pop = null;
  function closePop() { if (pop) { pop.remove(); pop = null; } }
  function openPop(a) {
    var g = G[a.getAttribute('data-t')];
    if (!g) return;
    closePop();
    pop = document.createElement('div');
    pop.className = 'tpop';
    var lecs = (g.lec || []).map(function (l) {
      return '<a class="gl" href="' + l + '.html">' + (LEC_LABEL[l] || l) + '</a>';
    }).join('');
    pop.innerHTML =
      '<div class="tpop-in">' +
      '<div class="tpop-h"><b>' + esc(g.zh) + '</b><span>' + esc(g.en) + '</span>' +
      '<button class="tpop-x" type="button" title="关闭">×</button></div>' +
      '<p class="tpop-s">' + esc(g.short) + '</p>' +
      (g.detail ? '<p class="tpop-d">' + esc(g.detail) + '</p>' : '') +
      '<p class="tpop-e"><b>例子</b>' + esc(g.example) + '</p>' +
      '<div class="tpop-f">' + lecs + '<a class="tpop-more" href="glossary.html#t-' + g.id + '">在术语表里看 →</a></div>' +
      '</div>';
    document.body.appendChild(pop);
    var r = a.getBoundingClientRect(), w = pop.offsetWidth, h = pop.offsetHeight;
    var left = Math.min(Math.max(12, r.left), window.innerWidth - w - 12);
    var top = r.bottom + 8;
    if (top + h > window.innerHeight - 12) top = Math.max(12, r.top - h - 8);
    pop.style.left = left + 'px';
    pop.style.top = top + 'px';
    pop.querySelector('.tpop-x').addEventListener('click', closePop);
  }
  document.addEventListener('click', function (e) {
    var t = e.target.closest && e.target.closest('a.term');
    if (t) { e.preventDefault(); openPop(t); return; }
    if (pop && !e.target.closest('.tpop')) closePop();
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closePop(); });

  // ------------------------------------------------- glossary page filter ---
  var gs = $('#gsearch');
  if (gs) {
    var chipOn = 'all';
    function applyG() {
      var q = gs.value.trim().toLowerCase();
      var n = 0;
      $$('.gentry').forEach(function (el) {
        var okQ = !q || (el.getAttribute('data-q') || '').indexOf(q) >= 0;
        var okL = chipOn === 'all' || (' ' + (el.getAttribute('data-lec') || '') + ' ').indexOf(' ' + chipOn + ' ') >= 0;
        var show = okQ && okL;
        el.hidden = !show;
        if (show) n++;
      });
      $('#gcount').textContent = n + ' 条';
      $('#gempty').hidden = n > 0;
    }
    gs.addEventListener('input', applyG);
    $$('.chip').forEach(function (c) {
      c.addEventListener('click', function () {
        $$('.chip').forEach(function (x) { x.classList.remove('on'); });
        c.classList.add('on');
        chipOn = c.getAttribute('data-lec');
        applyG();
      });
    });
    applyG();
  }

  // -------------------------------------------------------------- AI panel ---
  var panel = $('#ask-panel');
  if (!panel) return;

  var KEY_STORE = 'econ102.key', MODEL_STORE = 'econ102.model';
  var log = $('#ask-log'), text = $('#ask-text'), sendBtn = $('#ask-send');
  var setup = $('#ask-setup'), keyIn = $('#ask-key'), modelIn = $('#ask-model');
  var ctxBox = $('#ask-ctx');
  var history = [];   // {role, content}

  function getKey() { try { return localStorage.getItem(KEY_STORE) || ''; } catch (e) { return ''; } }
  function showSetup(on) {
    setup.hidden = !on;
    if (!on) { setup.hidden = true; }
  }
  if (getKey()) {
    setup.hidden = true;
    modelIn.value = localStorage.getItem(MODEL_STORE) || 'deepseek-chat';
  }
  $('#ask-save').addEventListener('click', function () {
    var k = keyIn.value.trim();
    if (!k) { keyIn.focus(); return; }
    try { localStorage.setItem(KEY_STORE, k); localStorage.setItem(MODEL_STORE, modelIn.value); } catch (e) {}
    setup.hidden = true;
    addMsg('sys', '可以问了。下面输入框里写问题，回车发送。');
  });
  modelIn.addEventListener('change', function () {
    try { localStorage.setItem(MODEL_STORE, modelIn.value); } catch (e) {}
  });

  function openPanel() {
    panel.classList.add('on');
    panel.setAttribute('aria-hidden', 'false');
    document.body.classList.add('asking');
    if (!log.childElementCount) {
      addMsg('sys', '我是这门课的助教。哪里没看懂，直接问，我会照着你正在看的这一页讲。');
    }
    setTimeout(function () { (getKey() ? text : keyIn).focus(); }, 60);
  }
  function closePanel() {
    panel.classList.remove('on');
    panel.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('asking');
  }
  $$('[data-ask]').forEach(function (b) { b.addEventListener('click', openPanel); });
  $('#ask-close').addEventListener('click', closePanel);

  function addMsg(who, content) {
    var d = document.createElement('div');
    d.className = 'msg ' + who;
    d.innerHTML = who === 'sys' ? esc(content) : lite(content);
    log.appendChild(d);
    log.scrollTop = log.scrollHeight;
    return d;
  }

  function pageContext() {
    var out = [];
    var h1 = $('.lec-hero h1');
    if (h1) out.push('正在读：' + h1.textContent.trim());
    if (slides.length) {
      var mid = window.innerHeight * 0.35, best = null, bd = 1e9;
      slides.forEach(function (s) {
        var r = s.getBoundingClientRect();
        var d = Math.abs(r.top - mid);
        if (d < bd) { bd = d; best = s; }
      });
      if (best) {
        var n = best.getAttribute('data-n');
        var t = $('.ptitle', best);
        var body = $('.teach', best);
        out.push('当前页：P' + n + (t ? ' ' + t.textContent.trim() : ''));
        if (body) out.push('这一页的讲义：' + body.textContent.replace(/\s+/g, ' ').slice(0, 1200));
      }
    }
    return out.join('\n');
  }

  function sysPrompt() {
    var p = '你是一位微观经济学助教，用的是浙江大学 ECON102 的讲义（教师 Mohan Zhou，教材 Acemoglu-Laibson-List《Economics》与 Landsburg）。' +
      '学生问什么就直答，先把机制讲清楚，再补一句例子或数字；能画图的地方描述一下图形怎么变。' +
      '中文口语，短句，别用「值得注意的是」「综上所述」这类空话，别写小标题党和总结段。一般不超过 350 字；学生追问细节时再展开。' +
      '如果问题与讲义无关，简单答，然后把他拉回正在学的内容。';
    if (ctxBox.checked) p += '\n\n【学生当前所在位置】\n' + pageContext();
    return p;
  }

  function push(role, content) {
    history.push({ role: role, content: content });
    if (history.length > 12) history = history.slice(-12);
  }

  var busy = false;
  async function send() {
    var q = text.value.trim();
    if (!q || busy) return;
    var key = getKey();
    if (!key) { setup.hidden = false; keyIn.focus(); return; }
    text.value = '';
    addMsg('me', q);
    var bubble = addMsg('bot', '');
    busy = true; sendBtn.disabled = true;
    var msgs = [{ role: 'system', content: sysPrompt() }].concat(history.slice(-6), [{ role: 'user', content: q }]);
    var acc = '';
    try {
      var res = await fetch('https://api.deepseek.com/chat/completions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key },
        body: JSON.stringify({ model: modelIn.value, messages: msgs, stream: true, temperature: 0.4 })
      });
      if (!res.ok) {
        var t = '';
        try { t = (await res.json()).error.message; } catch (e) {}
        throw new Error(res.status === 401 ? 'Key 不对或已失效（401）。点右上角设置重新填一个。'
          : res.status === 402 ? '账户余额不足（402）。'
          : '接口返回 ' + res.status + (t ? '：' + t : ''));
      }
      var reader = res.body.getReader(), dec = new TextDecoder(), buf = '';
      while (true) {
        var r = await reader.read();
        if (r.done) break;
        buf += dec.decode(r.value, { stream: true });
        var lines = buf.split('\n');
        buf = lines.pop();
        for (var i = 0; i < lines.length; i++) {
          var ln = lines[i].trim();
          if (!ln.startsWith('data:')) continue;
          var payload = ln.slice(5).trim();
          if (payload === '[DONE]') continue;
          try {
            var j = JSON.parse(payload);
            var d = j.choices && j.choices[0] && j.choices[0].delta && j.choices[0].delta.content;
            if (d) { acc += d; bubble.innerHTML = lite(acc); log.scrollTop = log.scrollHeight; }
          } catch (e) {}
        }
      }
      if (!acc) bubble.innerHTML = '<i>（没有返回内容，可能是模型超时，再发一次试试）</i>';
      else { push('user', q); push('assistant', acc); }
    } catch (err) {
      bubble.className = 'msg err';
      bubble.textContent = '出错了：' + (err && err.message ? err.message : err);
    } finally {
      busy = false; sendBtn.disabled = false;
    }
  }
  sendBtn.addEventListener('click', send);
  text.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && panel.classList.contains('on')) closePanel();
  });
})();
