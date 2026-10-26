import {Download, Maximize2} from 'lucide-react';
import {useLocale, useTranslations} from 'next-intl';
import type {Locale} from '@/i18n/routing';
import type {Presentation} from '@/lib/api-types';
import {fileSize} from '@/lib/format';
import {Button} from './Button';

/**
 * Презентация прямо на странице: file — всегда PDF, показываем встроенным просмотрщиком браузера.
 * Фрейм работает только на доменах из FRAME_ANCESTORS бэка, а на телефонах PDF во фрейме часто
 * не показывается — поэтому под ним «Открыть на весь экран». PPTX (source_file) — только скачать.
 */
export function PresentationViewer({
  file,
  sourceFile,
  title
}: {
  file: Presentation['file'];
  sourceFile: Presentation['source_file'];
  title: string;
}) {
  const t = useTranslations('Presentations');
  const tFiles = useTranslations('Attachments');
  const locale = useLocale() as Locale;
  const size = fileSize(file.size, locale);
  const sourceSize = sourceFile && fileSize(sourceFile.size, locale);

  return (
    <section>
      <div className="border border-border bg-surface p-1.5">
        <iframe
          src={`${file.url}#view=FitH`}
          title={t('viewerTitle', {title})}
          allowFullScreen
          className="block aspect-[4/3] w-full bg-primary-light sm:aspect-[16/10]"
        />
      </div>
      <div className="mt-4 flex flex-col gap-3 sm:flex-row">
        <Button href={file.url} target="_blank" rel="noopener noreferrer" variant={sourceFile ? 'secondary' : 'primary'}>
          <Maximize2 aria-hidden className="size-4" />
          {t('open')} · PDF
          {file.pages ? `, ${t('pages', {count: file.pages})}` : ''}, {size.value} {tFiles(`units.${size.unit}`)}
        </Button>
        {sourceFile && sourceSize && (
          // PPTX бэк отдаёт с Content-Disposition: attachment — скачается и с другого домена.
          <Button href={sourceFile.url} download>
            <Download aria-hidden className="size-4" />
            {t('download')} {sourceFile.ext.toUpperCase()}, {sourceSize.value} {tFiles(`units.${sourceSize.unit}`)}
          </Button>
        )}
      </div>
    </section>
  );
}
