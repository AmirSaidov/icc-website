import type {ReactNode} from 'react';
import {ArrowRight} from 'lucide-react';
import type {DirectionListItem} from '@/lib/api-types';
import {Card, CardLink} from './Card';
import {Icon} from './Icon';

/** Китайские цифры для нумерации направлений, как в макете: 一 … 十; дальше — арабские. */
const NUMERALS = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十'];
export const numeral = (index: number) => NUMERALS[index] ?? String(index + 1);

/** Квадрат в синей рамке: цифра 一…八 на главной, иконка — в разделе «Направления». */
function Mark({children}: {children: ReactNode}) {
  return (
    <span className="flex size-10 shrink-0 items-center justify-center rounded-sm border border-primary/70 bg-surface font-serif text-base text-primary transition-colors duration-300 group-has-[a.card-link:hover]:bg-primary group-has-[a.card-link:hover]:text-white">
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

/** Строка списка на главной: 一 | Название | →. */
export function DirectionRow({item, index}: {item: DirectionListItem; index: number}) {
  return (
    <article className="group relative flex items-center gap-4 border-b border-border py-4">
      <Mark>
        <span lang="zh-Hans" aria-hidden>
          {numeral(index)}
        </span>
      </Mark>
      <h3 className="min-w-0 flex-1 font-sans text-sm font-medium leading-snug text-navy md:text-[15px]">
        <CardLink href={`/directions/${item.slug}`}>{item.title}</CardLink>
      </h3>
      <ArrowRight
        aria-hidden
        className="size-4 shrink-0 text-muted transition-[color,transform] group-has-[a.card-link:hover]:translate-x-1 group-has-[a.card-link:hover]:text-primary"
      />
    </article>
  );
}
