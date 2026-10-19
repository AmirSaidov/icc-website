"use server";
import { hasLocale } from "next-intl";
import { routing } from "@/i18n/routing";
import { getEvents } from "@/lib/api";
import type { EventTypeCode, EventWhen } from "@/lib/api-types";
// Серверный экшен вызывается из браузера — аргументы не доверенные.
export async function loadMoreEvents(locale: string, when: EventWhen, type: EventTypeCode | undefined, page: number) {
    if (!hasLocale(routing.locales, locale) || !Number.isInteger(page) || page < 2) {
        throw new Error("Invalid arguments");
    }
    return getEvents(locale, { when: when === "past" ? "past" : "upcoming", type, page });
}
