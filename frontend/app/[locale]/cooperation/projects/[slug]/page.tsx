import type { Metadata } from "next";
import Image from "next/image";
import { notFound } from "next/navigation";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { PageHeader } from "@/components/ui/PageHeader";
import { RichText } from "@/components/ui/RichText";
import { Gallery } from "@/components/ui/Gallery";
import { Attachments } from "@/components/ui/Attachments";
import { PresentationCard } from "@/components/ui/PresentationCard";
import { SectionTitle } from "@/components/ui/SectionTitle";
import { formatDate } from "@/lib/format";
import { getProject } from "@/lib/api";
import { redirectToOwnSlug } from "@/lib/detail";
import { buildMetadata, detailPaths } from "@/lib/seo";
import type { Locale } from "@/i18n/routing";
export const revalidate = 60;
type Props = { params: Promise<{ locale: Locale; slug: string }> };
export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { locale, slug } = await params;
    const [item, t] = await Promise.all([
        getProject(locale, decodeURIComponent(slug)),
        getTranslations({ locale, namespace: "Cooperation" }),
    ]);
    if (!item) return {};
    return buildMetadata({
        locale,
        paths: detailPaths("cooperation/projects", item.seo.alternates),
        seo: item.seo,
        title: item.title ?? t("untranslated"),
        description: item.excerpt,
        image: item.cover?.large,
        noindex: !item.is_translated,
    });
}
export default async function ProjectDetail({ params }: Props) {
    const { locale, slug: rawSlug } = await params;
    const slug = decodeURIComponent(rawSlug);
    setRequestLocale(locale);
    const [item, t, nav] = await Promise.all([
        getProject(locale, slug),
        getTranslations("Cooperation"),
        getTranslations("Nav"),
    ]);
    if (!item) notFound();
    // Переключатель языка ведёт сюда со slug другого языка — редирект поправит адрес.
    redirectToOwnSlug(locale, "cooperation/projects", slug, item);
    const title = item.title ?? t("untranslated");
    return (
        <>
            <PageHeader
                title={title}
                lead={item.excerpt ?? undefined}
                breadcrumbs={[
                    { label: nav("cooperation"), href: "/cooperation" },
                    { label: title },
                ]}
            />
            <div className="container-page space-y-10 py-10">
                {item.is_translated ? (
                    <>
                        <p className="text-muted">
                            {item.country.name}
                            {item.published_at &&
                                ` · ${formatDate(item.published_at, locale)}`}
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
                        {item.partners.length > 0 && (
                            <section>
                                <SectionTitle>{t("partners")}</SectionTitle>
                                <ul data-reveal-stagger className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                                    {item.partners.map((p) => (
                                        <li
                                            key={p.id}
                                            className="rounded-lg border border-border p-4"
                                        >
                                            {p.website ? (
                                                <a
                                                    href={p.website}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="font-semibold text-primary"
                                                >
                                                    {p.name}
                                                </a>
                                            ) : (
                                                <p className="font-semibold">
                                                    {p.name}
                                                </p>
                                            )}
                                            {p.description && (
                                                <p className="mt-1 text-sm text-muted">
                                                    {p.description}
                                                </p>
                                            )}
                                        </li>
                                    ))}
                                </ul>
                            </section>
                        )}
                        {item.presentations.length > 0 && (
                            <section>
                                <SectionTitle>{nav("presentations")}</SectionTitle>
                                <ul data-reveal-stagger className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                                    {item.presentations.map((p) => (
                                        <li key={p.id} className="flex [&>*]:flex-1">
                                            <PresentationCard item={p} />
                                        </li>
                                    ))}
                                </ul>
                            </section>
                        )}
                        <Gallery images={item.gallery} />
                        <Attachments items={item.attachments} />
                    </>
                ) : (
                    <p className="text-muted">{t("untranslated")}</p>
                )}
            </div>
        </>
    );
}
