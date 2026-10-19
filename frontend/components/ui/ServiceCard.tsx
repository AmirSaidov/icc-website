import type {ServiceListItem} from '@/lib/api-types';
import {Card, CardLink} from './Card';

/** Карточка услуги в разделе «Услуги»: там заголовки карточек — h2 (под h1 страницы). */
export function ServiceCard({item, headingLevel = 'h2'}: {item: ServiceListItem; headingLevel?: 'h2' | 'h3'}) {
  const Heading = headingLevel;
  return (
    <Card className="gap-4 p-6">
      <Heading className="line-clamp-3 text-lg font-semibold leading-snug">
        <CardLink href={`/services/${item.slug}`}>{item.title}</CardLink>
      </Heading>
      <p className="line-clamp-4 text-sm text-muted">{item.short_text}</p>
    </Card>
  );
}
