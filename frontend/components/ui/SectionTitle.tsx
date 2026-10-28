import type {ReactNode} from 'react';
import {ArrowRight} from 'lucide-react';
import {Link} from '@/i18n/navigation';
import {cn} from '@/lib/cn';

interface SectionTitleProps {
  children: ReactNode;
  id?: string;
  /** Надзаголовок капсом: «ЧТО НАС ОБЪЕДИНЯЕТ». */
  eyebrow?: ReactNode;
  subtitle?: ReactNode;
  /** Ссылка справа: «Все новости →». */
  action?: {href: string; label: string};
  /** h2 по умолчанию; h1 на странице только один — в PageHeader. */
  as?: 'h2' | 'h3';
  align?: 'start' | 'center';
  /** На тёмном фоне (секция «Почему…»). */
  inverse?: boolean;
  className?: string;
}

/** Стрелка-ссылка «Все направления →» — и в заголовках секций, и под списками. */
export function ArrowLink({href, children, className}: {href: string; children: ReactNode; className?: string}) {
  return (
    <Link
      href={href}
      className={cn('group inline-flex shrink-0 items-center gap-1.5 text-sm font-semibold text-primary hover:underline', className)}
    >
      {children}
      <ArrowRight aria-hidden className="size-4 transition-transform group-hover:translate-x-1" />
    </Link>
  );
}

export function SectionTitle({
  children,
  id,
  eyebrow,
  subtitle,
  action,
  as: Tag = 'h2',
  align = 'start',
  inverse = false,
  className
}: SectionTitleProps) {
  const center = align === 'center';
  return (
    <div
      data-reveal
      className={cn(
        'mb-8 flex flex-wrap gap-x-6 gap-y-3 md:mb-12',
        center ? 'flex-col items-center text-center' : 'items-end justify-between',
        className
      )}
    >
      <div className={cn('min-w-0', center && 'max-w-3xl')}>
        {eyebrow && <p className={cn('eyebrow mb-3', inverse ? 'text-sky' : 'text-primary')}>{eyebrow}</p>}
        <Tag
          id={id}
          className={cn('text-[28px] font-extrabold leading-[1.1] md:text-[40px]', inverse ? 'text-white' : 'text-navy')}
        >
          {children}
        </Tag>
        {subtitle && <p className={cn('mt-3 max-w-2xl', inverse ? 'text-white/75' : 'text-muted', center && 'mx-auto')}>{subtitle}</p>}
      </div>
      {action && <ArrowLink href={action.href}>{action.label}</ArrowLink>}
    </div>
  );
}
