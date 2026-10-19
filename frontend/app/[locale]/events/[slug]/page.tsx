import type { Metadata } from "next";
import Image from "next/image";
import { notFound } from "next/navigation";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { SetAlternates } from "@/components/layout/Alternates";
import { PageHeader } from "@/components/ui/PageHeader";
import { RichText } from "@/components/ui/RichText";
import { Gallery } from "@/components/ui/Gallery";
import { Attachments } from "@/components/ui/Attachments";
import { EventCard } from "@/components/ui/EventCard";
import { formatDateRange } from "@/lib/format";
import { getEvent, getEvents } from "@/lib/api";
import { redirectToOwnSlug } from "@/lib/detail";
import { buildMetadata, detailPaths } from "@/lib/seo";
import type { Locale } from "@/i18n/routing";
export const revalidate = 60;
type Props = { params: Promise<{ locale: Locale; slug: string }> };
export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { locale, slug } = await params;
    const [item, t] = await Promise.all([
        getEvent(locale, decodeURIComponent(slug)),
        getTranslations({ locale, namespace: "Events" }),
    ]);
    if (!item) return {};
    return buildMetadata({
        locale,
        paths: detailPaths("events", item.seo.alternates),
        seo: item.seo,
        title: item.title ?? t("untranslated"),
        description: item.excerpt,
        image: item.cover?.large,
        noindex: !item.is_translated,
    });
}
export default async function EventDetail({ params }: Props) {
    const { locale, slug: rawSlug } = await params;
    const slug = decodeURIComponent(rawSlug);
    setRequestLocale(locale);
    const [item, upcoming, t, nav] = await Promise.all([
        getEvent(locale, slug),
        getEvents(locale, { when: "upcoming", pageSize: 4 }),
        getTranslations("Events"),
        getTranslations("Nav"),
    ]);
    if (!item) notFound();
    redirectToOwnSlug(locale, "events", slug, item);
    // Отдельного «похожие» в API нет — показываем ближайшие, кроме текущего.
    const related = upcoming.results.filter((x) => x.id !== item.id).slice(0, 3);
    const title = item.title ?? t("untranslated");
    return (
        <>
            <SetAlternates section="events" slugs={item.seo.alternates} />
            <PageHeader
                title={title}
                lead={item.excerpt ?? undefined}
                breadcrumbs={[
                    { label: nav("events"), href: "/events" },
                    { label: title },
                ]}
            />
            <div className="container-page space-y-10 py-10">
                {item.is_translated ? (
                    <>
                        <p className="text-muted">
                            {item.type.label} ·{" "}
                            {formatDateRange(
                                item.start_at,
                                item.end_at ?? null,
                                locale,
                            )}
                            {item.location ? ` · ${item.location}` : ""}
                        </p>
                        {item.cover && (
                            <div className="relative aspect-[16/9] overflow-hidden rounded-lg">
                                <Image
                                    src={item.cover.large}
                                    alt={item.title ?? ""}
                                    fill
                                    priority
                                    sizes="(min-width: 1200px) 1200px, 100vw"
                                    className="object-cover"
                                />
                            </div>
                        )}
                        {item.content && <RichText html={item.content} />}
                        <Gallery images={item.gallery} />
                        <Attachments items={item.attachments} />
                    </>
                ) : (
                    <p className="text-muted">{t("untranslated")}</p>
                )}
                {related.length > 0 && (
                    <section>
                        <h2 className="mb-5 text-2xl font-bold">
                            {t("related")}
                        </h2>
                        <ul data-reveal-stagger className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                            {related.map((x) => (
                                <li key={x.id} className="flex [&>*]:flex-1">
                                    <EventCard item={x} />
                                </li>
                            ))}
                        </ul>
                    </section>
                )}
            </div>
        </>
    );
}
