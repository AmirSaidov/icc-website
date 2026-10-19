'use client';

import {useLocale, useTranslations} from 'next-intl';
import type {NewsCategory, NewsListItem} from '@/lib/api-types';
import {loadMoreNews} from '@/app/[locale]/news/actions';
import {FilterSelect} from './FilterSelect';
import {LoadMoreButton, useLoadMore} from './LoadMore';
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
  const locale = useLocale();
  const t = useTranslations('News');
  const {items, more, pending, failed, loadMore} = useLoadMore(initial, hasMore, (page) =>
    loadMoreNews(locale, category, page)
  );

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
        <LoadMoreButton
          pending={pending}
          failed={failed}
          onClick={loadMore}
          label={t('loadMore')}
          loadingLabel={t('loading')}
        />
      )}
    </>
  );
}
