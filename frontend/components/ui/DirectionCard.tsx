import type {DirectionListItem} from '@/lib/api-types';
import {Card, CardLink} from './Card';
import {Icon} from './Icon';

/** Карточка направления: Главная (4 шт.) и раздел «Направления» (8 шт.). */
export function DirectionCard({item, headingLevel = 'h3'}: {item: DirectionListItem; headingLevel?: 'h2' | 'h3'}) {
  const Heading = headingLevel;
  return (
    <Card className="gap-4 p-6">
      <span className="flex size-12 items-center justify-center rounded-md bg-primary-light text-primary transition-colors duration-300 group-has-[a.card-link:hover]:bg-primary group-has-[a.card-link:hover]:text-white">
        <Icon name={item.icon} className="size-6" />
      </span>
      <Heading className="line-clamp-3 text-lg font-semibold leading-snug">
        <CardLink href={`/directions/${item.slug}`}>{item.title}</CardLink>
      </Heading>
      <p className="line-clamp-4 text-sm text-muted">{item.short_text}</p>
    </Card>
  );
}
