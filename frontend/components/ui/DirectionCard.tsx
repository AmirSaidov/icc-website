import type {ReactNode} from 'react';
import {ArrowRight} from 'lucide-react';
import type {DirectionListItem} from '@/lib/api-types';
import {Card, CardLink} from './Card';
import {Icon} from './Icon';

/** Номер направления на главной: 01, 02, … */
const numeral = (index: number) => String(index + 1).padStart(2, '0');

/** Полоска над плиткой на главной — по очереди три цвета знака. */
const ACCENTS = ['bg-seal', 'bg-sun', 'bg-brand-blue'];

/** Иконка направления в разделе «Направления». */
function Mark({children}: {children: ReactNode}) {
  return (
    <span className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-primary-light text-primary transition-colors duration-300 group-has-[a.card-link:hover]:bg-primary group-has-[a.card-link:hover]:text-white">
      {children}
    </span>
  );
}

/** Карточка направления в разделе «Направления». */
export function DirectionCard({item, headingLevel = 'h3'}: {item: DirectionListItem; headingLevel?: 'h2' | 'h3'}) {
  const Heading = headingLevel;
  return (
    <Card className="gap-4 p-6">
      <Mark>
        <Icon name={item.icon} className="size-5" />
      </Mark>
      <Heading className="line-clamp-3 text-lg font-bold leading-snug text-navy">
        <CardLink href={`/directions/${item.slug}`}>{item.title}</CardLink>
      </Heading>
      <p className="line-clamp-4 text-sm text-muted">{item.short_text}</p>
    </Card>
  );
}

/** Плитка на главной: цветная полоска, номер, название, стрелка. */
export function DirectionTile({item, index}: {item: DirectionListItem; index: number}) {
  return (
    <Card className="h-full justify-between gap-10 p-6">
      <div className="flex items-center justify-between">
        <span aria-hidden className="flex items-center gap-3 text-sm font-bold tabular-nums text-muted">
          <span className={`h-1.5 w-8 rounded-full ${ACCENTS[index % ACCENTS.length]}`} />
          {numeral(index)}
        </span>
        <span
          aria-hidden
          className="flex size-9 items-center justify-center rounded-full border border-border text-navy transition-[background-color,border-color,color,rotate] duration-300 group-has-[a.card-link:hover]:-rotate-45 group-has-[a.card-link:hover]:border-primary group-has-[a.card-link:hover]:bg-primary group-has-[a.card-link:hover]:text-white"
        >
          <ArrowRight className="size-4" />
        </span>
      </div>
      <h3 className="text-lg font-bold leading-snug text-navy">
        <CardLink href={`/directions/${item.slug}`}>{item.title}</CardLink>
      </h3>
    </Card>
  );
}
