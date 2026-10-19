"use server";
import { hasLocale } from "next-intl";
import { routing } from "@/i18n/routing";
import { getNews } from "@/lib/api";
// Серверный экшен вызывается из браузера — аргументы не доверенные.
export async function loadMoreNews(locale: string, category: string, page: number) {
    if (!hasLocale(routing.locales, locale) || !Number.isInteger(page) || page < 2) {
        throw new Error("Invalid arguments");
    }
    return getNews(locale, { category: category || undefined, page });
}
