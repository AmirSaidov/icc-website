import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { CtaBlock } from "@/components/sections/CtaBlock";
import { SetAlternates } from "@/components/layout/Alternates";
import { PageHeader } from "@/components/ui/PageHeader";
import { RichText } from "@/components/ui/RichText";
import type { Locale } from "@/i18n/routing";
import { getDirection } from "@/lib/api";
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
        description: item.summary,
        noindex: !item.is_translated,
    });
}
export default async function DirectionPage({ params }: Props) {
    const { locale, slug } = await params;
    setRequestLocale(locale);
    const [item, t, nav] = await Promise.all([
        getDirection(locale, decodeURIComponent(slug)),
        getTranslations("Directions"),
        getTranslations("Nav"),
    ]);
    if (!item) notFound();
    return (
        <>
            <SetAlternates section="directions" slugs={item.seo.alternates} />
            <PageHeader
                title={item.title}
                lead={item.summary}
                breadcrumbs={[
                    { label: nav("directions"), href: "/directions" },
                    { label: item.title },
                ]}
            />
            {item.is_translated ? (
                <main className="container-page space-y-10 py-12">
                    <RichText html={item.content} />
                </main>
            ) : (
                <main className="container-page py-12">
                    <p className="text-muted">{t("untranslated")}</p>
                </main>
            )}
            <CtaBlock />
        </>
    );
}
