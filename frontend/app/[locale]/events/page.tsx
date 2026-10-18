import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { PageHeader } from "@/components/ui/PageHeader";
import { EventCard } from "@/components/ui/EventCard";
import { Link } from "@/i18n/navigation";
import { getEvents } from "@/lib/api";
import { buildMetadata, staticPaths } from "@/lib/seo";
import type { EventStatus, EventType } from "@/lib/api-types";
import type { Locale } from "@/i18n/routing";
export const revalidate = 60;
type Props = {
    params: Promise<{ locale: Locale }>;
    searchParams: Promise<{ status?: string; type?: string }>;
};
const types: EventType[] = ["mission", "forum", "exhibition", "b2b"];
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
export default async function EventsPage({ params, searchParams }: Props) {
    const { locale } = await params;
    const query = await searchParams;
    const status: EventStatus = query.status === "past" ? "past" : "upcoming";
    const type = types.find((x) => x === query.type);
    setRequestLocale(locale);
    const [data, t, nav, eventTypes] = await Promise.all([
        getEvents(locale, { status, type }),
        getTranslations("Events"),
        getTranslations("Nav"),
        getTranslations("EventTypes"),
    ]);
    return (
        <>
            <PageHeader
                title={t("title")}
                lead={t("description")}
                breadcrumbs={[{ label: nav("events") }]}
            />
            <main className="container-page py-12">
                <div className="mb-8 flex flex-wrap gap-3">
                    <Link
                        className={`rounded px-4 py-2 ${status === "upcoming" ? "bg-primary text-white" : "border border-border"}`}
                        href={type ? `/events?type=${type}` : "/events"}
                    >
                        {t("upcoming")}
                    </Link>
                    <Link
                        className={`rounded px-4 py-2 ${status === "past" ? "bg-primary text-white" : "border border-border"}`}
                        href={
                            type
                                ? `/events?status=past&type=${type}`
                                : "/events?status=past"
                        }
                    >
                        {t("past")}
                    </Link>
                    <Link
                        className="rounded border border-border px-4 py-2"
                        href={
                            status === "past"
                                ? "/events?status=past"
                                : "/events"
                        }
                    >
                        {t("allTypes")}
                    </Link>
                    {types.map((v) => (
                        <Link
                            key={v}
                            className={`rounded border border-border px-4 py-2 ${type === v ? "bg-primary-light" : ""}`}
                            href={`/events?${status === "past" ? "status=past&" : ""}type=${v}`}
                        >
                            {eventTypes(v)}
                        </Link>
                    ))}
                </div>
                {data.results.length ? (
                    <ul className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                        {data.results.map((item) => (
                            <li key={item.id} className="flex [&>*]:flex-1">
                                <EventCard item={item} />
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="text-muted">{t("empty")}</p>
                )}
            </main>
        </>
    );
}
