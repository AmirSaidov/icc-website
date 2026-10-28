import {cn} from '@/lib/cn';

/** Фирменные цвета знака (брендбук, лист 27). */
export const BRAND = {
  red: '#FF4D4D',
  yellow: '#FFC22E',
  blue: '#2F6BFF'
} as const;

/** «C»: кольцо R 105 / r 51 с вырезом 90° вправо. Центр кольца — точка (0, 0). */
export const C_PATH = 'M74.25-74.25A105 105 0 1 0 74.25 74.25L36.06 36.06A51 51 0 1 1 36.06-36.06Z';

/** Три коротких полоски цветами знака — подпись над заголовками. */
export function BrandStripe({className}: {className?: string}) {
  return (
    <span aria-hidden className={cn('flex gap-1', className)}>
      <span className="h-1.5 w-5 rounded-full bg-seal" />
      <span className="h-1.5 w-5 rounded-full bg-sun" />
      <span className="h-1.5 w-5 rounded-full bg-brand-blue" />
    </span>
  );
}

/**
 * Знак ЦПК: красная и синяя «C», между ними жёлтая планка.
 * Цвета смешиваются как краски (multiply) — отсюда тёмно-зелёный и почти чёрный в пересечениях.
 * На тёмном фоне — screen, как в брендбуке: пересечение светлеет.
 */
export function BrandMark({inverse = false, className}: {inverse?: boolean; className?: string}) {
  const blend = {mixBlendMode: inverse ? 'screen' : 'multiply'} as const;
  return (
    <svg viewBox="0 0 305 210" aria-hidden focusable="false" className={cn('shrink-0', className)}>
      <g style={{isolation: 'isolate'}}>
        <path d={C_PATH} transform="translate(105 105)" fill={BRAND.red} style={blend} />
        <rect x="141" y="10" width="54" height="190" fill={BRAND.yellow} style={blend} />
        <path d={C_PATH} transform="translate(230 105)" fill={BRAND.blue} style={blend} />
      </g>
    </svg>
  );
}
