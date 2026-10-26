import Image from 'next/image';
import {Presentation} from 'lucide-react';
import {useLocale, useTranslations} from 'next-intl';
import type {Locale} from '@/i18n/routing';
import type {PresentationShort} from '@/lib/api-types';
import {fileSize, formatDate} from '@/lib/format';
import {CardLink} from './Card';
import {CARD_IMAGE_SIZES} from './NewsCard';

/**
 * Как карточка новости: превью в рамке (нет превью — иконка), «раздел · дата», заголовок, PDF, страницы и размер.
 * Подходит и для списка, и для Project.presentations — у них общие поля.
 */
export function PresentationCard({item, headingLevel = 'h3'}: {item: PresentationShort; headingLevel?: 'h2' | 'h3'}) {
  const t = useTranslations('Presentations');
  const tFiles = useTranslations('Attachments');
  const locale = useLocale() as Locale;
  const Heading = headingLevel;
  const size = fileSize(item.file.size, locale);

  return (
    <article className="group relative flex flex-col gap-3">
      <div className="border border-border bg-surface p-1.5 transition-colors duration-300 group-has-[a.card-link:hover]:border-primary/40">
        <div className="relative flex aspect-[3/2] items-center justify-center overflow-hidden bg-primary-light">
          {item.cover ? (
            <Image
              src={item.cover.small}
              alt={item.title ?? ''}
              fill
              sizes={CARD_IMAGE_SIZES}
              className="object-cover transition-transform duration-500 group-has-[a.card-link:hover]:scale-105"
            />
          ) : (
            <Presentation aria-hidden className="size-14 text-primary/60" strokeWidth={1.25} />
          )}
        </div>
      </div>
      <div className="flex min-w-0 flex-1 flex-col gap-1.5">
        <p className="text-xs font-semibold text-primary">
          {/* «Промышленность и IT» уточняем сферой: «Информационные технологии · дата». */}
          {(item.category === 'industry' && item.sector?.name) || t(`categories.${item.category}`)}
          {item.published_at && (
            <>
              {' · '}
              <time dateTime={item.published_at}>{formatDate(item.published_at, locale)}</time>
            </>
          )}
        </p>
        <Heading className="line-clamp-3 text-lg font-bold leading-snug text-navy">
          <CardLink href={`/presentations/${item.slug}`}>{item.title}</CardLink>
        </Heading>
        {item.excerpt && <p className="line-clamp-3 text-sm text-muted">{item.excerpt}</p>}
        <p className="mt-auto text-xs text-muted">
          PDF{item.file.pages ? `, ${t('pages', {count: item.file.pages})}` : ''}, {size.value} {tFiles(`units.${size.unit}`)}
        </p>
      </div>
    </article>
  );
}
