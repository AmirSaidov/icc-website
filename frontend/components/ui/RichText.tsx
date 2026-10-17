import {cn} from '@/lib/cn';

/**
 * HTML из CMS. Санитизация — на бэке (Айбек), сюда приходит уже чистый HTML.
 * Таблицы оборачиваются, чтобы на 360 px прокручивались сами, а не страница.
 */
export function RichText({html, className}: {html: string; className?: string}) {
  if (!html) return null;
  const prepared = html
    .replace(/<table/g, '<div class="table-wrap"><table')
    .replace(/<\/table>/g, '</table></div>');
  return <div className={cn('rich-text', className)} dangerouslySetInnerHTML={{__html: prepared}} />;
}
