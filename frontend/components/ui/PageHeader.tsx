import type {ReactNode} from 'react';
import {Breadcrumbs, type Crumb} from './Breadcrumbs';

/** Шапка внутренней страницы: хлебные крошки, единственный h1, вводный текст; орнамент снизу. */
export function PageHeader({
  title,
  lead,
  breadcrumbs,
  children
}: {
  title: string;
  lead?: string;
  breadcrumbs: Crumb[];
  children?: ReactNode;
}) {
  return (
    <section>
      <div className="container-page py-10 md:py-14">
        <Breadcrumbs items={breadcrumbs} />
        <h1 className="mt-4 max-w-3xl text-3xl font-bold leading-tight text-navy motion-safe:animate-fade-up md:text-[40px]">
          {title}
        </h1>
        {lead && <p className="mt-4 max-w-2xl text-lg text-muted motion-safe:animate-fade-up motion-safe:[animation-delay:100ms]">{lead}</p>}
        {children}
      </div>
      <div aria-hidden className="ornament-band" />
    </section>
  );
}
