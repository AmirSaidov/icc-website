import type {ServiceListItem} from '@/lib/api-types';
import {Card,CardLink} from './Card';

export function ServiceCard({item}:{item:ServiceListItem}){return <Card className="gap-4 p-6"><h2 className="line-clamp-3 text-lg font-semibold leading-snug"><CardLink href={`/services/${item.slug}`}>{item.title}</CardLink></h2><p className="line-clamp-4 text-sm text-muted">{item.short_text}</p></Card>;}
