/* Shared, progressive enhancements. All content and destination links are static. */
(function () {
  'use strict';
  var root = document.documentElement;
  var languageButtons = document.querySelectorAll('[data-set-lang]');
  var status = document.createElement('div');
  status.className = 'site-status';
  status.setAttribute('role', 'status');
  status.setAttribute('aria-live', 'polite');
  document.body.appendChild(status);
  var statusTimer;
  function say(en, zh) {
    status.textContent = root.dataset.lang === 'zh' ? zh : en;
    status.classList.add('visible');
    clearTimeout(statusTimer);
    statusTimer = setTimeout(function () { status.classList.remove('visible'); }, 4500);
  }
  function setLanguage(lang, remember) {
    lang = lang === 'zh' ? 'zh' : 'en';
    root.dataset.lang = lang;
    root.lang = lang === 'zh' ? 'zh-Hant-TW' : 'en';
    languageButtons.forEach(function (button) {
      button.setAttribute('aria-pressed', String(button.dataset.setLang === lang));
    });
    if (remember) {
      try { localStorage.setItem('site-lang', lang); } catch (_) {}
      try {
        var url = new URL(location.href);
        url.searchParams.set('lang', lang);
        history.replaceState(null, '', url);
      } catch (_) {}
    }
    // Carry the language across local pages even when localStorage is blocked.
    document.querySelectorAll('a[href]').forEach(function (link) {
      var href = link.getAttribute('href');
      if (/^(?:[\w-]+\.html)(?:[?#]|$)/.test(href)) {
        var parts = href.split('#');
        var path = parts[0].split('?')[0];
        var params = new URLSearchParams(parts[0].split('?')[1] || '');
        params.set('lang', lang);
        link.setAttribute('href', path + '?' + params.toString() + (parts.length > 1 ? '#' + parts[1] : ''));
      }
    });
  }
  languageButtons.forEach(function (button) {
    button.addEventListener('click', function () { setLanguage(button.dataset.setLang, true); });
  });
  setLanguage(root.dataset.lang, false);

  var menu = document.querySelector('.menu-toggle');
  var nav = document.querySelector('.topbar nav');
  function closeMenu() {
    if (!menu || !nav) return;
    menu.setAttribute('aria-expanded', 'false');
    nav.classList.remove('is-open');
  }
  if (menu && nav) {
    menu.addEventListener('click', function () {
      var open = menu.getAttribute('aria-expanded') !== 'true';
      menu.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('is-open', open);
    });
    nav.querySelectorAll('a').forEach(function (link) { link.addEventListener('click', closeMenu); });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') {
        closeMenu(); menu.focus();
      }
    });
    document.addEventListener('click', function (event) {
      if (!event.target.closest('.topbar')) closeMenu();
    });
  }

  async function copyText(value, button) {
    var copied = false;
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(value);
        copied = true;
      }
    } catch (_) { /* Try local-file and restricted-permission fallback. */ }
    if (!copied) {
      var textarea = document.createElement('textarea');
      textarea.value = value;
      textarea.setAttribute('readonly', '');
      textarea.style.cssText = 'position:fixed;top:0;left:0;opacity:0;pointer-events:none';
      var parent = document.querySelector('dialog[open]') || document.body;
      parent.appendChild(textarea);
      textarea.select();
      try { copied = document.execCommand('copy'); } catch (_) {}
      textarea.remove();
      if (button) button.focus();
    }
    if (copied) {
      say('Copied to clipboard.', '已複製到剪貼簿。');
    } else {
      say('Copy is unavailable. Please select and copy the visible link or citation.', '無法自動複製，請選取顯示的網址或引用內容手動複製。');
    }
  }
  document.querySelectorAll('[data-copy-value], [data-copy-target]').forEach(function (button) {
    button.addEventListener('click', function () {
      var source = document.getElementById(button.dataset.copyTarget);
      var value = button.dataset.copyValue || (source && source.textContent.trim());
      if (value) copyText(value, button);
    });
  });

  // Native dialog gives Escape, modal focus management, and focus restoration.
  var dialog = document.getElementById('image-dialog');
  if (dialog && typeof dialog.showModal === 'function') {
    var image = dialog.querySelector('img');
    var title = dialog.querySelector('#image-dialog-title');
    var destination = dialog.querySelector('[data-dialog-destination]');
    var opener;
    document.querySelectorAll('a[data-enlarge]').forEach(function (link) {
      link.addEventListener('click', function (event) {
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        opener = link;
        var thumb = link.querySelector('img');
        image.src = link.getAttribute('href');
        image.alt = thumb ? thumb.alt : '';
        title.textContent = link.dataset.title || image.alt;
        destination.hidden = !link.dataset.destination;
        if (link.dataset.destination) {
          destination.href = link.dataset.destination;
          destination.textContent = link.dataset.destination;
        }
        dialog.showModal();
      });
    });
    dialog.querySelector('[data-dialog-close]').addEventListener('click', function () { dialog.close(); });
    dialog.addEventListener('click', function (event) {
      if (event.target !== dialog) return;
      var r = dialog.getBoundingClientRect();
      if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close();
    });
    dialog.addEventListener('close', function () { if (opener) opener.focus(); });
  }

  // Highlight a section only on the homepage, without hijacking anchor navigation.
  if ('IntersectionObserver' in window && document.querySelector('main.content')) {
    var sectionObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting || !nav) return;
        nav.querySelectorAll('a').forEach(function (link) {
          if (link.getAttribute('href') === '#' + entry.target.id) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        });
      });
    }, { rootMargin: '-10% 0px -65% 0px', threshold: 0 });
    document.querySelectorAll('main.content > section[id]').forEach(function (section) { sectionObserver.observe(section); });
  }
})();
