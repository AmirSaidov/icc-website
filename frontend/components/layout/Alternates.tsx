'use client';

import {createContext, useContext, useEffect, useState, type ReactNode} from 'react';
import type {LocaleSlugs} from '@/lib/api-types';
import type {DetailSection} from './nav';

type Alternates = {section: DetailSection; slugs: LocaleSlugs} | null;

const AlternatesContext = createContext<{
  alternates: Alternates;
  setAlternates: (value: Alternates) => void;
}>({alternates: null, setAlternates: () => {}});

/** Оборачивает шапку и страницу в layout, чтобы детальная страница могла передать slug'и переключателю языка. */
export function AlternatesProvider({children}: {children: ReactNode}) {
  const [alternates, setAlternates] = useState<Alternates>(null);
  return <AlternatesContext.Provider value={{alternates, setAlternates}}>{children}</AlternatesContext.Provider>;
}

export const useAlternates = () => useContext(AlternatesContext).alternates;

/**
 * Ставится на каждой детальной странице (news, events, services, directions):
 *
 *   <SetAlternates section="news" slugs={item.seo.alternates} />
 *
 * Тогда RU/EN/中文 в шапке ведут на ту же запись на другом языке,
 * а если перевода нет — на список раздела.
 */
export function SetAlternates({section, slugs}: {section: DetailSection; slugs: LocaleSlugs}) {
  const {setAlternates} = useContext(AlternatesContext);
  const key = JSON.stringify(slugs);
  useEffect(() => {
    setAlternates({section, slugs: JSON.parse(key)});
    return () => setAlternates(null);
  }, [section, key, setAlternates]);
  return null;
}
