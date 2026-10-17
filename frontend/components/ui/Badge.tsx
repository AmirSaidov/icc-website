import type {ReactNode} from 'react';
import {cn} from '@/lib/cn';

type Tone = 'primary' | 'neutral' | 'inverse';

const tones: Record<Tone, string> = {
  primary: 'bg-primary-light text-primary',
  neutral: 'border border-border bg-surface text-muted',
  inverse: 'bg-primary text-white'
};

/** Категория новости, тип мероприятия. */
export function Badge({tone = 'primary', className, children}: {tone?: Tone; className?: string; children: ReactNode}) {
  return (
    <span className={cn('inline-flex items-center rounded px-2 py-0.5 text-xs font-medium', tones[tone], className)}>
      {children}
    </span>
  );
}
