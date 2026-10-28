import type {ComponentProps, ReactNode} from 'react';
import {Link} from '@/i18n/navigation';
import {cn} from '@/lib/cn';

/** inverse и inverse-outline — для тёмного фона (CtaBlock, первый экран). */
type Variant = 'primary' | 'secondary' | 'link' | 'inverse' | 'inverse-outline';
type Size = 'md' | 'lg';

const base =
  'inline-flex items-center justify-center gap-2 font-semibold transition-[color,background-color,border-color,transform] duration-200 active:scale-[0.97] disabled:pointer-events-none disabled:opacity-60';

const variants: Record<Variant, string> = {
  primary: 'rounded-full bg-primary text-white shadow-[0_8px_20px_-10px_rgb(37_93_240/0.7)] hover:bg-primary-hover',
  secondary: 'rounded-full border border-navy/15 bg-surface text-navy hover:border-navy/40',
  link: 'text-primary underline-offset-4 hover:underline',
  inverse: 'rounded-full bg-white text-navy hover:bg-primary-light',
  'inverse-outline': 'rounded-full border border-white/30 text-white hover:border-white/60 hover:bg-white/10'
};

const sizes: Record<Size, string> = {
  md: 'min-h-10 px-5 text-[13px]',
  lg: 'min-h-12 px-7 text-sm'
};

export function buttonClass({variant = 'primary', size = 'md', className}: {variant?: Variant; size?: Size; className?: string} = {}) {
  return cn(base, variants[variant], variant !== 'link' && sizes[size], className);
}

type CommonProps = {variant?: Variant; size?: Size; className?: string; children: ReactNode};

/** Внешние ссылки, файлы, tel: и mailto: — обычный <a>, внутренние — Link с префиксом языка. */
const isExternal = (href: string) => /^(https?:|mailto:|tel:|\/\/)/.test(href) || /\.\w{2,4}$/.test(href);

type ButtonAsLink = CommonProps & {href: string} & Omit<ComponentProps<'a'>, 'href' | 'className' | 'children'>;
type ButtonAsButton = CommonProps & {href?: undefined} & Omit<ComponentProps<'button'>, 'className' | 'children'>;

export function Button(props: ButtonAsLink | ButtonAsButton) {
  const {variant, size, className, children, ...rest} = props;
  const classes = buttonClass({variant, size, className});

  if (rest.href !== undefined) {
    const {href, ...anchorProps} = rest as ButtonAsLink;
    return isExternal(href) ? (
      <a href={href} className={classes} {...anchorProps}>
        {children}
      </a>
    ) : (
      <Link href={href} className={classes} {...anchorProps}>
        {children}
      </Link>
    );
  }

  const {type = 'button', ...buttonProps} = rest as ButtonAsButton;
  return (
    <button type={type} className={classes} {...buttonProps}>
      {children}
    </button>
  );
}
