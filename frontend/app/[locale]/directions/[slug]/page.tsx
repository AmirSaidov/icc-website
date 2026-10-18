import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { CtaBlock } from "@/components/sections/CtaBlock";
import { SetAlternates } from "@/components/layout/Alternates";
import { PageHeader } from "@/components/ui/PageHeader";
import { RichText } from "@/components/ui/RichText";
import type { Locale } from "@/i18n/routing";
import { getDirection } from "@/lib/api";
import { redirectToOwnSlug } from "@/lib/detail";
import { buildMetadata, detailPaths } from "@/lib/seo";

export const revalidate = 60;
type Props = { params: Promise<{ locale: Locale; slug: string }> };
export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { locale, slug } = await params;
    const item = await getDirection(locale, decodeURIComponent(slug));
    if (!item) return {};
    return buildMetadata({
        locale,
        paths: detailPaths("directions", item.seo.alternates),
        seo: item.seo,
        title: item.title,
        description: item.short_text,
        noindex: !item.is_translated,
    });
}
export default async function DirectionPage({ params }: Props) {
    const { locale, slug: rawSlug } = await params;
    const slug = decodeURIComponent(rawSlug);
    setRequestLocale(locale);
    const [item, t, nav] = await Promise.all([
        getDirection(locale, slug),
        getTranslations("Directions"),
        getTranslations("Nav"),
    ]);
    if (!item) notFound();
    redirectToOwnSlug(locale, "directions", slug, item);
    const title = item.title ?? t("untranslated");
    return (
        <>
            <SetAlternates section="directions" slugs={item.seo.alternates} />
            <PageHeader
                title={title}
                lead={item.short_text ?? undefined}
                breadcrumbs={[
                    { label: nav("directions"), href: "/directions" },
                    { label: title },
                ]}
            />
            <div className="container-page space-y-10 py-12">
                {item.is_translated ? (
                    item.content && <RichText html={item.content} />
                ) : (
                    <p className="text-muted">{t("untranslated")}</p>
                )}
            </div>
            <CtaBlock />
        </>
    );
}
