/* Apply a valid language before paint; query links also work without storage. */
(function () {
  var lang = 'en';
  try { lang = localStorage.getItem('site-lang') || 'en'; } catch (_) {}
  var requested = new URLSearchParams(location.search).get('lang');
  if (requested === 'en' || requested === 'zh') lang = requested;
  lang = lang === 'zh' ? 'zh' : 'en';
  document.documentElement.dataset.lang = lang;
  document.documentElement.lang = lang === 'zh' ? 'zh-Hant-TW' : 'en';
  document.documentElement.classList.add('js');
})();
