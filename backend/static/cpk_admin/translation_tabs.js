/* Подписи языковых вкладок modeltranslation: «ru / en / zh» → «RU / EN / 中文». */
(function () {
  var LABELS = { ru: "RU", en: "EN", zh: "中文" };
  var SELECTOR = ".ui-tabs-nav a, #modeltranslation-main-switch option";

  function relabel() {
    Array.prototype.forEach.call(document.querySelectorAll(SELECTOR), function (node) {
      var label = LABELS[node.textContent.trim()];
      if (label) {
        node.textContent = label;
      }
    });
  }

  // Вкладки строятся скриптом modeltranslation (и заново для новых inline-строк),
  // поэтому следим за DOM, а не за конкретным событием загрузки.
  // relabel идемпотентен и дешёв; собственные правки текста дают ещё один вызов без изменений.
  var observer = new MutationObserver(relabel);

  document.addEventListener("DOMContentLoaded", function () {
    relabel();
    observer.observe(document.body, { childList: true, subtree: true });
  });
})();
