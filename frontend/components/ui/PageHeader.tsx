import type {ReactNode} from 'react';
import {Breadcrumbs, type Crumb} from './Breadcrumbs';

/** Шапка внутренней страницы: хлебные крошки, единственный h1, вводный текст. */
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
    <section className="border-b border-border bg-primary-light">
      <div className="container-page py-8 md:py-12">
        <Breadcrumbs items={breadcrumbs} />
        <h1 className="mt-4 max-w-4xl text-3xl font-bold leading-tight motion-safe:animate-fade-up md:text-4xl">{title}</h1>
        {lead && <p className="mt-4 max-w-3xl text-lg text-muted motion-safe:animate-fade-up motion-safe:[animation-delay:100ms]">{lead}</p>}
        {children}
      </div>
    </section>
  );
}
