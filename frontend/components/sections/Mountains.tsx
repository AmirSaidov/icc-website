import {cn} from '@/lib/cn';

/**
 * Горы Тянь-Шаня с красным солнцем (макет «Тянь-Шань»). Чистый SVG, без картинок:
 * три гряды от светлой к тёмной, снег на вершинах, низ растворяется в фоне страницы.
 * id — префикс для градиентов, если на странице несколько экземпляров.
 */
export function Mountains({id = 'mtn', sun = true, className}: {id?: string; sun?: boolean; className?: string}) {
  const g = (name: string) => `${id}-${name}`;
  return (
    <svg
      aria-hidden
      viewBox="0 0 800 450"
      preserveAspectRatio="xMaxYMax meet"
      className={cn('pointer-events-none select-none', className)}
    >
      <defs>
        <linearGradient id={g('far')} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#c9d5eb" />
          <stop offset="1" stopColor="#eef2f9" />
        </linearGradient>
        <linearGradient id={g('mid')} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#7f9ad0" />
          <stop offset="0.7" stopColor="#d3ddef" />
        </linearGradient>
        <linearGradient id={g('near')} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#2f4f8f" />
          <stop offset="0.55" stopColor="#9fb3dc" />
          <stop offset="1" stopColor="#e6ecf6" />
        </linearGradient>
        {/* Низ уходит в фон: белое — видно, чёрное — прозрачно. */}
        <linearGradient id={g('fade')} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0.62" stopColor="#fff" />
          <stop offset="1" stopColor="#000" />
        </linearGradient>
        {/* Левый край тоже растворяется — без резкой вертикальной границы рядом с текстом. */}
        <linearGradient id={g('fade-x')} x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor="#000" />
          <stop offset="0.22" stopColor="#fff" />
        </linearGradient>
        <mask id={g('mask')} maskUnits="userSpaceOnUse" x="0" y="0" width="800" height="450">
          <rect width="800" height="450" fill={`url(#${g('fade')})`} />
        </mask>
        <mask id={g('mask-x')} maskUnits="userSpaceOnUse" x="0" y="0" width="800" height="450">
          <rect width="800" height="450" fill={`url(#${g('fade-x')})`} />
        </mask>
      </defs>

      {sun && <circle cx="585" cy="92" r="46" fill="#cd4337" />}

      <g mask={`url(#${g('mask-x')})`}>
      <g mask={`url(#${g('mask')})`}>
        {/* Дальняя гряда */}
        <polygon
          fill={`url(#${g('far')})`}
          points="0,450 0,330 70,262 118,292 190,172 238,214 300,96 340,122 402,40 462,142 520,112 602,192 660,160 742,232 800,204 800,450"
        />
        {/* Снег */}
        <polygon fill="#fff" fillOpacity="0.95" points="402,40 383,72 393,67 401,82 410,67 421,73" />
        <polygon fill="#fff" fillOpacity="0.9" points="300,96 287,119 296,114 302,126 309,113 314,118" />
        <polygon fill="#fff" fillOpacity="0.85" points="520,112 508,124 516,122 522,130 528,121" />

        {/* Средняя гряда */}
        <polygon
          fill={`url(#${g('mid')})`}
          opacity="0.9"
          points="60,450 132,330 172,352 252,250 302,300 362,214 432,312 482,268 562,334 622,282 702,334 762,302 800,318 800,450"
        />

        {/* Ближняя, самая тёмная */}
        <polygon
          fill={`url(#${g('near')})`}
          points="0,450 0,404 62,362 112,386 182,300 242,352 302,322 352,372 422,326 502,392 582,350 652,388 732,344 800,376 800,450"
        />
      </g>
      </g>

      {/* Птицы */}
      <path d="M648 236q7-8 14 0M676 226q6-7 12 0" fill="none" stroke="#2b4880" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}
