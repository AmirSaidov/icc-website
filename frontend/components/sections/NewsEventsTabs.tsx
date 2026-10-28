import {useTranslations} from 'next-intl';
import {Link} from '@/i18n/navigation';
import {cn} from '@/lib/cn';

/** Пункт меню «Новости и мероприятия» ведёт на /news — отсюда же переход на /events и обратно. */
export function NewsEventsTabs({current}: {current: 'news' | 'events'}) {
  const tNews = useTranslations('News');
  const tEvents = useTranslations('Events');
  const tabs = [
    {key: 'news', href: '/news', label: tNews('title')},
    {key: 'events', href: '/events', label: tEvents('title')}
  ] as const;

  return (
    <ul className="mt-6 flex flex-wrap gap-2">
      {tabs.map((tab) => {
        const active = tab.key === current;
        return (
          <li key={tab.key}>
            <Link
              href={tab.href}
              aria-current={active ? 'page' : undefined}
              className={cn(
                'inline-flex min-h-10 items-center rounded-full px-4 text-sm font-medium transition-colors',
                active ? 'bg-primary text-white' : 'border border-primary/30 bg-surface text-primary hover:bg-primary-light'
              )}
            >
              {tab.label}
            </Link>
          </li>
        );
      })}
    </ul>
  );
}
