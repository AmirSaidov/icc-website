import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { PageHeader } from "@/components/ui/PageHeader";
import { EventCard } from "@/components/ui/EventCard";
import { Link } from "@/i18n/navigation";
import { getEvents, getEventTypes } from "@/lib/api";
import { buildMetadata, staticPaths } from "@/lib/seo";
import type { EventWhen } from "@/lib/api-types";
import type { Locale } from "@/i18n/routing";
export const revalidate = 60;
// Читает searchParams (фильтры) — рендерится на каждый запрос; ответы API всё равно кэшируются на 60 с.
export const dynamic = "force-dynamic";
type Props = {
    params: Promise<{ locale: Locale }>;
    searchParams: Promise<{ when?: string; type?: string }>;
};
export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { locale } = await params;
    const t = await getTranslations({ locale, namespace: "Events" });
    return buildMetadata({
        locale,
        paths: staticPaths("/events"),
        title: t("title"),
        description: t("description"),
    });
}
/** /events?when=past&type=forum — без пустых параметров. */
function eventsHref(when: EventWhen, type?: string) {
    const params = new URLSearchParams();
    if (when === "past") params.set("when", "past");
    if (type) params.set("type", type);
    const qs = params.toString();
    return qs ? `/events?${qs}` : "/events";
}
export default async function EventsPage({ params, searchParams }: Props) {
    const { locale } = await params;
    const query = await searchParams;
    const when: EventWhen = query.when === "past" ? "past" : "upcoming";
    setRequestLocale(locale);
    const [eventTypes, t, nav] = await Promise.all([
        getEventTypes(locale),
        getTranslations("Events"),
        getTranslations("Nav"),
    ]);
    // Неизвестный type бэк отклоняет с 400 — пропускаем только коды из /event-types/.
    const type = eventTypes.find((x) => x.code === query.type)?.code;
    const data = await getEvents(locale, { when, type });
    return (
        <>
            <PageHeader
                title={t("title")}
                lead={t("description")}
                breadcrumbs={[{ label: nav("events") }]}
            />
            <div className="container-page py-12">
                <div className="mb-8 flex flex-wrap gap-3">
                    <Link
                        className={`rounded px-4 py-2 ${when === "upcoming" ? "bg-primary text-white" : "border border-border"}`}
                        href={eventsHref("upcoming", type)}
                    >
                        {t("upcoming")}
                    </Link>
                    <Link
                        className={`rounded px-4 py-2 ${when === "past" ? "bg-primary text-white" : "border border-border"}`}
                        href={eventsHref("past", type)}
                    >
                        {t("past")}
                    </Link>
                    <Link
                        className={`rounded border border-border px-4 py-2 ${!type ? "bg-primary-light" : ""}`}
                        href={eventsHref(when)}
                    >
                        {t("allTypes")}
                    </Link>
                    {eventTypes.map((v) => (
                        <Link
                            key={v.code}
                            className={`rounded border border-border px-4 py-2 ${type === v.code ? "bg-primary-light" : ""}`}
                            href={eventsHref(when, v.code)}
                        >
                            {v.label}
                        </Link>
                    ))}
                </div>
                {data.results.length ? (
                    <ul data-reveal-stagger className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                        {data.results.map((item) => (
                            <li key={item.id} className="flex [&>*]:flex-1">
                                <EventCard item={item} />
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="text-muted">{t("empty")}</p>
                )}
            </div>
        </>
    );
}
