'use client';

import {useState, useTransition} from 'react';
import {useLocale, useTranslations} from 'next-intl';
import type {Locale} from '@/i18n/routing';
import type {NewsCategory, NewsListItem} from '@/lib/api-types';
import {loadMoreNews} from '@/app/[locale]/news/actions';
import {Button} from './Button';
import {FilterSelect} from './FilterSelect';
import {NewsCard} from './NewsCard';

/** Фильтр по категории + сетка новостей + «Загрузить ещё». На странице ставится с key={category}. */
export function NewsList({
  initial,
  categories,
  category,
  hasMore
}: {
  initial: NewsListItem[];
  categories: NewsCategory[];
  category: string;
  hasMore: boolean;
}) {
  const locale = useLocale() as Locale;
  const t = useTranslations('News');
  const [items, setItems] = useState(initial);
  const [page, setPage] = useState(2);
  const [more, setMore] = useState(hasMore);
  const [pending, start] = useTransition();

  const loadMore = () =>
    start(async () => {
      const next = await loadMoreNews(locale, category, page);
      setItems((current) => [...current, ...next.results]);
      setPage((value) => value + 1);
      setMore(Boolean(next.next));
    });

  return (
    <>
      {categories.length > 0 && (
        <div className="mb-8">
          <FilterSelect
            param="category"
            label={t('category')}
            allLabel={t('allCategories')}
            value={category}
            options={categories
              .filter((c) => c.slug && c.name)
              .map((c) => ({value: c.slug!, label: c.name!}))}
          />
        </div>
      )}
      {items.length ? (
        <ul data-reveal-stagger className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((item) => (
            <li key={item.id} className="flex [&>*]:flex-1">
              <NewsCard item={item} />
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-muted">{t('empty')}</p>
      )}
      {more && (
        <div className="mt-8 text-center">
          <Button disabled={pending} onClick={loadMore}>
            {pending ? t('loading') : t('loadMore')}
          </Button>
        </div>
      )}
    </>
  );
}
