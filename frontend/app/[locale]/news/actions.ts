"use server";
import type { Locale } from "@/i18n/routing";
import { getNews } from "@/lib/api";
export async function loadMoreNews(
    locale: Locale,
    category: string,
    page: number,
) {
    return getNews(locale, { category: category || undefined, page });
}
