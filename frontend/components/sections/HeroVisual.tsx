import type {CSSProperties, ReactNode} from 'react';
import {Factory, Globe, Handshake} from 'lucide-react';
import {BRAND, C_PATH} from '@/components/ui/BrandMark';
import {cn} from '@/lib/cn';

/** Точки на орбитах: угол в градусах и цвет. */
const OUTER_DOTS = [
  {angle: -30, color: BRAND.red, r: 7},
  {angle: 95, color: BRAND.blue, r: 5},
  {angle: 200, color: BRAND.yellow, r: 8}
];
const INNER_DOTS = [
  {angle: 40, color: BRAND.yellow, r: 5},
  {angle: 250, color: BRAND.red, r: 4}
];

const polar = (radius: number, angle: number) => ({
  cx: Math.round(radius * Math.cos((angle * Math.PI) / 180) * 100) / 100,
  cy: Math.round(radius * Math.sin((angle * Math.PI) / 180) * 100) / 100
});

const multiply = {mixBlendMode: 'multiply'} as const;

function Chip({className, delay, children}: {className: string; delay: string; children: ReactNode}) {
  return (
    <div
      aria-hidden
      style={{animationDelay: delay} as CSSProperties}
      className={cn(
        'hero-float absolute flex items-center gap-2.5 rounded-2xl bg-white p-2.5 shadow-[0_18px_40px_-18px_rgb(18_21_30/0.35)] ring-1 ring-black/5',
        className
      )}
    >
      {children}
    </div>
  );
}

/**
 * Первый экран, справа: знак «CC» собирается из двух колец и планки,
 * затем кольца поворачиваются навстречу друг другу, как сцепленные шестерни.
 * Только SVG и CSS (globals.css, .hero-*). При «уменьшить движение» — статичная картинка.
 */
export function HeroVisual({className}: {className?: string}) {
  return (
    <div className={cn('relative mx-auto aspect-square w-full max-w-[540px]', className)}>
      <svg viewBox="0 0 600 600" aria-hidden focusable="false" className="size-full overflow-visible">
        <defs>
          <pattern id="hero-dots" width="18" height="18" patternUnits="userSpaceOnUse">
            <circle cx="2" cy="2" r="1.4" fill="#12151e" fillOpacity="0.14" />
          </pattern>
          <radialGradient id="hero-fade">
            <stop offset="0.35" stopColor="#fff" />
            <stop offset="1" stopColor="#fff" stopOpacity="0" />
          </radialGradient>
          <mask id="hero-mask">
            <circle cx="300" cy="300" r="300" fill="url(#hero-fade)" />
          </mask>
        </defs>

        {/* Подложка: точечная сетка, гаснущая к краям, и орбиты */}
        <rect width="600" height="600" fill="url(#hero-dots)" mask="url(#hero-mask)" />
        <circle cx="300" cy="300" r="286" fill="none" stroke="#12151e" strokeOpacity="0.12" strokeDasharray="2 8" strokeLinecap="round" />
        <circle cx="300" cy="300" r="232" fill="none" stroke="#12151e" strokeOpacity="0.08" />

        <g transform="translate(300 300)">
          <g className="hero-orbit">
            {OUTER_DOTS.map(({angle, color, r}) => (
              <circle key={angle} {...polar(286, angle)} r={r} fill={color} />
            ))}
          </g>
          <g className="hero-orbit hero-orbit-reverse">
            {INNER_DOTS.map(({angle, color, r}) => (
              <circle key={angle} {...polar(232, angle)} r={r} fill={color} />
            ))}
          </g>
        </g>

        {/* Знак: 305×210 × 1.35, по центру */}
        <g transform="translate(94 158) scale(1.35)" style={{isolation: 'isolate'}}>
          <g className="hero-in-left" style={multiply}>
            <g transform="translate(105 105)">
              <path className="hero-tick" style={{'--dir': -1} as CSSProperties} d={C_PATH} fill={BRAND.red} />
            </g>
          </g>
          <g className="hero-in-grow" style={multiply}>
            <rect x="141" y="10" width="54" height="190" fill={BRAND.yellow} />
          </g>
          <g className="hero-in-right" style={multiply}>
            <g transform="translate(230 105)">
              <path className="hero-tick" style={{'--dir': 1} as CSSProperties} d={C_PATH} fill={BRAND.blue} />
            </g>
          </g>
        </g>
      </svg>

      <Chip className="left-[2%] top-[14%]" delay="0s">
        <span className="flex size-10 items-center justify-center rounded-xl bg-brand-blue text-white">
          <Factory className="size-5" strokeWidth={1.75} />
        </span>
      </Chip>
      <Chip className="right-[1%] top-[24%]" delay="-2s">
        <span className="flex size-10 items-center justify-center rounded-xl bg-seal text-white">
          <Handshake className="size-5" strokeWidth={1.75} />
        </span>
      </Chip>
      <Chip className="bottom-[12%] left-[10%]" delay="-4s">
        <span className="flex size-10 items-center justify-center rounded-xl bg-sun text-navy">
          <Globe className="size-5" strokeWidth={1.75} />
        </span>
      </Chip>
    </div>
  );
}
