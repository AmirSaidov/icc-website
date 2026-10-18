'use client';

import {useEffect} from 'react';

const SELECTOR = '[data-reveal]:not(.is-visible), [data-reveal-stagger] > :not(.is-visible)';
/** Шаг задержки между карточками сетки; после 6-й задержка начинается заново («Загрузить ещё»). */
const STAGGER_MS = 70;

/**
 * Добавляет .is-visible элементам с data-reveal (и детям data-reveal-stagger), когда они
 * въезжают в экран. Стили — в globals.css. Новые элементы (переход по страницам,
 * «Загрузить ещё») подхватывает MutationObserver.
 */
export function RevealObserver() {
  useEffect(() => {
    const io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      },
      {rootMargin: '0px 0px -8% 0px', threshold: 0.08}
    );

    const scan = () => {
      document.querySelectorAll<HTMLElement>(SELECTOR).forEach((el) => {
        const parent = el.parentElement;
        if (parent?.hasAttribute('data-reveal-stagger')) {
          const index = Array.prototype.indexOf.call(parent.children, el);
          el.style.setProperty('--reveal-delay', `${(index % 6) * STAGGER_MS}ms`);
        }
        io.observe(el);
      });
    };

    let frame = 0;
    const mo = new MutationObserver(() => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(scan);
    });

    scan();
    mo.observe(document.body, {childList: true, subtree: true});
    return () => {
      cancelAnimationFrame(frame);
      io.disconnect();
      mo.disconnect();
    };
  }, []);

  return null;
}
