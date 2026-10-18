import type {ServiceListItem} from '@/lib/api-types';
import {Card,CardLink} from './Card';
import {Icon} from './Icon';

export function ServiceCard({item}:{item:ServiceListItem}){return <Card className="gap-4 p-6"><span className="flex size-12 items-center justify-center rounded-md bg-primary-light text-primary"><Icon name={item.icon} className="size-6"/></span><h2 className="line-clamp-3 text-lg font-semibold leading-snug"><CardLink href={`/services/${item.slug}`}>{item.title}</CardLink></h2><p className="line-clamp-4 text-sm text-muted">{item.summary}</p></Card>;}
