import type {ReactNode} from 'react';
import {ArrowRight} from 'lucide-react';
import {Link} from '@/i18n/navigation';
import {cn} from '@/lib/cn';

interface SectionTitleProps {
  children: ReactNode;
  id?: string;
  subtitle?: ReactNode;
  /** Ссылка справа: «Все новости →». */
  action?: {href: string; label: string};
  /** h2 по умолчанию; h1 на странице только один — в PageHeader. */
  as?: 'h2' | 'h3';
  className?: string;
}

export function SectionTitle({children, id, subtitle, action, as: Tag = 'h2', className}: SectionTitleProps) {
  return (
    <div className={cn('mb-6 flex flex-wrap items-end justify-between gap-x-6 gap-y-2 md:mb-8', className)}>
      <div className="min-w-0">
        <Tag id={id} className="text-2xl font-bold leading-tight text-text md:text-3xl">
          {children}
        </Tag>
        {subtitle && <p className="mt-2 max-w-2xl text-muted">{subtitle}</p>}
      </div>
      {action && (
        <Link
          href={action.href}
          className="inline-flex shrink-0 items-center gap-1 text-sm font-medium text-primary hover:underline"
        >
          {action.label}
          <ArrowRight aria-hidden className="size-4" />
        </Link>
      )}
    </div>
  );
}
