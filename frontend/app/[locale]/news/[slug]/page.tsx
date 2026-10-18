import type { Metadata } from "next";
import Image from "next/image";
import { notFound } from "next/navigation";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { SetAlternates } from "@/components/layout/Alternates";
import { PageHeader } from "@/components/ui/PageHeader";
import { RichText } from "@/components/ui/RichText";
import { Gallery } from "@/components/ui/Gallery";
import { Attachments } from "@/components/ui/Attachments";
import { NewsCard } from "@/components/ui/NewsCard";
import { formatDate } from "@/lib/format";
import { getNewsItem } from "@/lib/api";
import { buildMetadata, detailPaths } from "@/lib/seo";
import type { Locale } from "@/i18n/routing";
export const revalidate = 60;
type Props = { params: Promise<{ locale: Locale; slug: string }> };
export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { locale, slug } = await params;
    const item = await getNewsItem(locale, decodeURIComponent(slug));
    if (!item) return {};
    return buildMetadata({
        locale,
        paths: detailPaths("news", item.seo.alternates),
        seo: item.seo,
        title: item.title,
        description: item.summary,
        image: item.cover?.url,
        noindex: !item.is_translated,
    });
}
export default async function NewsDetail({ params }: Props) {
    const { locale, slug } = await params;
    setRequestLocale(locale);
    const [item, t, nav] = await Promise.all([
        getNewsItem(locale, decodeURIComponent(slug)),
        getTranslations("News"),
        getTranslations("Nav"),
    ]);
    if (!item) notFound();
    return (
        <>
            <SetAlternates section="news" slugs={item.seo.alternates} />
            <PageHeader
                title={item.title}
                breadcrumbs={[
                    { label: nav("news"), href: "/news" },
                    { label: item.title },
                ]}
            />
            <main className="container-page space-y-10 py-10">
                {item.is_translated ? (
                    <>
                        <time
                            className="text-muted"
                            dateTime={item.published_at}
                        >
                            {formatDate(item.published_at, locale)}
                        </time>
                        {item.cover && (
                            <div className="relative aspect-[16/9] overflow-hidden rounded-lg">
                                <Image
                                    src={item.cover.url}
                                    alt={item.cover.alt}
                                    fill
                                    priority
                                    sizes="(min-width: 1200px) 1200px, 100vw"
                                    className="object-cover"
                                />
                            </div>
                        )}
                        <RichText html={item.content} />
                        <Gallery images={item.gallery} />
                        <Attachments items={item.attachments} />
                    </>
                ) : (
                    <p className="text-muted">{t("untranslated")}</p>
                )}
                {item.related.length > 0 && (
                    <section>
                        <h2 className="mb-5 text-2xl font-bold">
                            {t("related")}
                        </h2>
                        <ul className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                            {item.related.slice(0, 3).map((x) => (
                                <li key={x.id} className="flex [&>*]:flex-1">
                                    <NewsCard item={x} />
                                </li>
                            ))}
                        </ul>
                    </section>
                )}
            </main>
        </>
    );
}
