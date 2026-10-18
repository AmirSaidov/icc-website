import type {ComponentProps, ReactNode} from 'react';
import {Link} from '@/i18n/navigation';
import {cn} from '@/lib/cn';

/** inverse и inverse-outline — для тёмного фона (CtaBlock, первый экран). */
type Variant = 'primary' | 'secondary' | 'link' | 'inverse' | 'inverse-outline';
type Size = 'md' | 'lg';

const base =
  'inline-flex items-center justify-center gap-2 font-medium transition-[color,background-color,border-color,transform] duration-200 active:scale-[0.97] disabled:pointer-events-none disabled:opacity-60';

const variants: Record<Variant, string> = {
  primary: 'rounded-md bg-primary text-white hover:bg-primary-hover',
  secondary: 'rounded-md border border-primary bg-white text-primary hover:bg-primary-light',
  link: 'text-primary underline-offset-4 hover:underline',
  inverse: 'rounded-md bg-white text-primary hover:bg-primary-light',
  'inverse-outline': 'rounded-md border border-white text-white hover:bg-white/10'
};

const sizes: Record<Size, string> = {
  md: 'min-h-10 px-4 text-sm',
  lg: 'min-h-12 px-6 text-base'
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
