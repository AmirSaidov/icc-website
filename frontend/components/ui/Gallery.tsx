'use client';

import {useCallback, useEffect, useRef, useState} from 'react';
import Image from 'next/image';
import {ChevronLeft, ChevronRight, X} from 'lucide-react';
import {useTranslations} from 'next-intl';
import type {ImageAsset} from '@/lib/api-types';
import {SectionTitle} from './SectionTitle';

/** Сетка превью + просмотр в lightbox (<dialog>: фокус, Esc и затемнение из коробки). */
export function Gallery({images, title}: {images: ImageAsset[]; title?: string}) {
  const t = useTranslations('Gallery');
  const dialogRef = useRef<HTMLDialogElement>(null);
  const [index, setIndex] = useState<number | null>(null);
  const total = images.length;

  const open = (i: number) => {
    setIndex(i);
    dialogRef.current?.showModal();
  };
  const close = () => dialogRef.current?.close();
  const step = useCallback(
    (delta: number) => setIndex((i) => (i === null ? i : (i + delta + total) % total)),
    [total]
  );

  useEffect(() => {
    if (index === null) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'ArrowLeft') step(-1);
      if (event.key === 'ArrowRight') step(1);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [index, step]);

  if (!total) return null;
  const current = index !== null ? images[index] : null;

  return (
    <section>
      <SectionTitle>{title ?? t('title')}</SectionTitle>
      <ul className="grid grid-cols-2 gap-3 md:grid-cols-3">
        {images.map((image, i) => (
          <li key={image.url}>
            <button
              type="button"
              onClick={() => open(i)}
              className="relative block aspect-[3/2] w-full overflow-hidden rounded-md bg-primary-light"
              aria-label={t('open', {index: i + 1, total})}
            >
              <Image
                src={image.url}
                alt={image.alt}
                fill
                sizes="(min-width: 768px) 33vw, 50vw"
                className="object-cover transition-transform hover:scale-105"
              />
            </button>
          </li>
        ))}
      </ul>

      <dialog
        ref={dialogRef}
        onClose={() => setIndex(null)}
        onClick={(event) => event.target === dialogRef.current && close()}
        className="m-auto h-dvh max-h-none w-screen max-w-none bg-transparent p-0 backdrop:bg-black/85"
      >
        {current && (
          <div className="flex h-full flex-col items-center justify-center gap-3 p-4" onClick={(e) => e.target === e.currentTarget && close()}>
            <div className="relative h-[75dvh] w-full max-w-5xl">
              <Image src={current.url} alt={current.alt} fill sizes="100vw" className="object-contain" />
            </div>
            <p className="max-w-3xl text-center text-sm text-white/90">
              {current.alt} · {t('counter', {index: (index ?? 0) + 1, total})}
            </p>
            <button type="button" onClick={close} aria-label={t('close')} className="absolute right-4 top-4 rounded-full bg-white/10 p-2 text-white hover:bg-white/20">
              <X aria-hidden className="size-6" />
            </button>
            {total > 1 && (
              <>
                <button type="button" onClick={() => step(-1)} aria-label={t('prev')} className="absolute left-2 top-1/2 -translate-y-1/2 rounded-full bg-white/10 p-2 text-white hover:bg-white/20 md:left-6">
                  <ChevronLeft aria-hidden className="size-7" />
                </button>
                <button type="button" onClick={() => step(1)} aria-label={t('next')} className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full bg-white/10 p-2 text-white hover:bg-white/20 md:right-6">
                  <ChevronRight aria-hidden className="size-7" />
                </button>
              </>
            )}
          </div>
        )}
      </dialog>
    </section>
  );
}
