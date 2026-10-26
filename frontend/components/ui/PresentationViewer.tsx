import {Download, Maximize2} from 'lucide-react';
import {useLocale, useTranslations} from 'next-intl';
import type {Locale} from '@/i18n/routing';
import type {Attachment} from '@/lib/api-types';
import {fileSize} from '@/lib/format';
import {Button} from './Button';

/** PowerPoint браузер сам не показывает — открываем через Office Online (файл должен быть доступен из интернета). */
const OFFICE_EXT = ['ppt', 'pptx'];
const officeUrl = (mode: 'embed' | 'view', url: string) =>
  `https://view.officeapps.live.com/op/${mode}.aspx?src=${encodeURIComponent(url)}`;

/**
 * Презентация прямо на странице: PDF — встроенным просмотрщиком браузера, PPT/PPTX — через Office Online.
 * Под ней «Открыть на весь экран» и «Скачать»: на телефонах PDF во фрейме часто не показывается.
 */
export function PresentationViewer({file, title}: {file: Attachment; title: string}) {
  const t = useTranslations('Presentations');
  const tFiles = useTranslations('Attachments');
  const locale = useLocale() as Locale;
  const ext = file.ext.toLowerCase();
  const isOffice = OFFICE_EXT.includes(ext);
  const embedSrc = ext === 'pdf' ? `${file.url}#view=FitH` : isOffice ? officeUrl('embed', file.url) : null;
  const size = fileSize(file.size, locale);

  return (
    <section>
      {embedSrc ? (
        <div className="border border-border bg-surface p-1.5">
          <iframe
            src={embedSrc}
            title={t('viewerTitle', {title})}
            allowFullScreen
            className="block aspect-[4/3] w-full bg-primary-light sm:aspect-[16/10]"
          />
        </div>
      ) : (
        <p className="border border-border bg-surface p-6 text-muted">{t('noPreview')}</p>
      )}
      <div className="mt-4 flex flex-col gap-3 sm:flex-row">
        {embedSrc && (
          <Button
            href={isOffice ? officeUrl('view', file.url) : file.url}
            target="_blank"
            rel="noopener noreferrer"
            variant="secondary"
          >
            <Maximize2 aria-hidden className="size-4" />
            {t('open')}
          </Button>
        )}
        <Button href={file.url} download>
          <Download aria-hidden className="size-4" />
          {t('download')} · {ext.toUpperCase()}, {size.value} {tFiles(`units.${size.unit}`)}
        </Button>
      </div>
    </section>
  );
}
