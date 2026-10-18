'use client';

import {useTransition} from 'react';
import {usePathname, useRouter} from '@/i18n/navigation';
import {cn} from '@/lib/cn';
import {Select, type SelectOption} from './Select';

/**
 * Фильтр списка через параметр адреса: /cooperation?country=CN (других параметров на этих страницах нет).
 * Пустое значение («Все …») убирает параметр. Пока страница грузится, список полупрозрачный.
 */
export function FilterSelect({
  param,
  label,
  allLabel,
  value,
  options
}: {
  param: string;
  label: string;
  allLabel: string;
  value: string;
  options: SelectOption[];
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [pending, startTransition] = useTransition();

  const onChange = (next: string) => {
    const href = next ? `${pathname}?${new URLSearchParams({[param]: next})}` : pathname;
    startTransition(() => router.push(href, {scroll: false}));
  };

  return (
    <Select
      label={label}
      value={value}
      options={[{value: '', label: allLabel}, ...options]}
      onChange={onChange}
      className={cn('transition-opacity', pending && 'opacity-60')}
    />
  );
}
