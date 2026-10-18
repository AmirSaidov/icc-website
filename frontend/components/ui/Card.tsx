import type {ComponentProps, ElementType, ReactNode} from 'react';
import {Link} from '@/i18n/navigation';
import {cn} from '@/lib/cn';

type CardProps<T extends ElementType> = {
  as?: T;
  className?: string;
  children: ReactNode;
} & Omit<ComponentProps<T>, 'as' | 'className' | 'children'>;

/** Белая карточка с рамкой. Если внутри есть CardLink — кликабельна целиком. */
export function Card<T extends ElementType = 'article'>({as, className, children, ...rest}: CardProps<T>) {
  const Tag = as ?? 'article';
  return (
    <Tag
      className={cn(
        'group relative flex flex-col overflow-hidden rounded-lg border border-border bg-surface transition-[box-shadow,transform,border-color] duration-300 has-[a.card-link:hover]:-translate-y-1 has-[a.card-link:hover]:border-primary/30 has-[a.card-link:hover]:shadow-lg has-[a.card-link:focus-visible]:shadow-lg',
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
