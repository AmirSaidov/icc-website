import type {ComponentProps, ElementType, ReactNode} from 'react';
import {Link} from '@/i18n/navigation';
import {cn} from '@/lib/cn';

type CardProps<T extends ElementType> = {
  as?: T;
  className?: string;
  children: ReactNode;
} & Omit<ComponentProps<T>, 'as' | 'className' | 'children'>;

/** Белая карточка с тонкой рамкой и прямыми углами. Если внутри есть CardLink — кликабельна целиком. */
export function Card<T extends ElementType = 'article'>({as, className, children, ...rest}: CardProps<T>) {
  const Tag = as ?? 'article';
  return (
    <Tag
      className={cn(
        'group relative flex flex-col overflow-hidden rounded-sm border border-border bg-surface transition-[box-shadow,transform,border-color] duration-300 has-[a.card-link:hover]:-translate-y-0.5 has-[a.card-link:hover]:border-primary/40 has-[a.card-link:hover]:shadow-[0_10px_30px_-12px_rgb(21_40_79/0.25)] has-[a.card-link:focus-visible]:shadow-lg',
        className
      )}
      {...rest}
    >
      {children}
    </Tag>
  );
}

/**
 * Ссылка заголовка, растянутая на всю карточку (::after), — один таб-стоп
 * и понятный текст ссылки для скринридера.
 */
export function CardLink({href, className, children}: {href: string; className?: string; children: ReactNode}) {
  return (
    <Link
      href={href}
      className={cn(
        'card-link after:absolute after:inset-0 after:content-[""] hover:text-primary focus-visible:outline-none',
        className
      )}
    >
      {children}
    </Link>
  );
}
