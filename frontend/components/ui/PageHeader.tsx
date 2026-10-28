import type {ReactNode} from 'react';
import {BrandStripe} from './BrandMark';
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
    <section className="border-b border-border bg-surface">
      <div className="container-page py-10 md:py-16">
        <Breadcrumbs items={breadcrumbs} />
        <BrandStripe className="mt-8 motion-safe:animate-fade-up" />
        <h1 className="mt-4 max-w-4xl text-[34px] font-extrabold leading-[1.08] text-navy motion-safe:animate-fade-up md:text-[52px]">
          {title}
        </h1>
        {lead && (
          <p className="mt-5 max-w-2xl text-lg leading-relaxed text-muted motion-safe:animate-fade-up motion-safe:[animation-delay:100ms]">
            {lead}
          </p>
        )}
        {children}
      </div>
    </section>
  );
}
