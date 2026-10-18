import {Download, FileText} from 'lucide-react';
import {useLocale, useTranslations} from 'next-intl';
import type {Locale} from '@/i18n/routing';
import type {Attachment} from '@/lib/api-types';
import {fileSize} from '@/lib/format';
import {SectionTitle} from './SectionTitle';

/** Список файлов с типом и размером: «PDF, 56,4 КБ». */
export function Attachments({items, title}: {items: Attachment[]; title?: string}) {
  const t = useTranslations('Attachments');
  const locale = useLocale() as Locale;
  if (!items.length) return null;

  return (
    <section>
      <SectionTitle>{title ?? t('title')}</SectionTitle>
      <ul className="divide-y divide-border rounded-lg border border-border">
        {items.map((file) => {
          const size = fileSize(file.size, locale);
          return (
            <li key={file.url}>
              <a
                href={file.url}
                download
                className="flex items-center gap-4 p-4 transition-colors hover:bg-primary-light"
              >
                <FileText aria-hidden className="size-8 shrink-0 text-primary" strokeWidth={1.5} />
                <span className="min-w-0 flex-1">
                  <span className="block font-medium break-words">{file.title ?? file.url.split('/').pop()}</span>
                  <span className="text-sm text-muted">
                    {file.ext.toUpperCase()}, {size.value} {t(`units.${size.unit}`)}
                  </span>
                </span>
                <Download aria-hidden className="size-5 shrink-0 text-primary" />
                <span className="sr-only">{t('download')}</span>
              </a>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
