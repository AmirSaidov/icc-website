import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { SetAlternates } from "@/components/layout/Alternates";
import { CtaBlock } from "@/components/sections/CtaBlock";
import { PageHeader } from "@/components/ui/PageHeader";
import { RichText } from "@/components/ui/RichText";
import { Button } from "@/components/ui/Button";
import { SectionTitle } from "@/components/ui/SectionTitle";
import type { Locale } from "@/i18n/routing";
import { getService } from "@/lib/api";
import { redirectToOwnSlug } from "@/lib/detail";
import { buildMetadata, detailPaths } from "@/lib/seo";
export const revalidate = 60;
type Props = { params: Promise<{ locale: Locale; slug: string }> };
export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { locale, slug } = await params;
    const [item, t] = await Promise.all([
        getService(locale, decodeURIComponent(slug)),
        getTranslations({ locale, namespace: "Services" }),
    ]);
    if (!item) return {};
    return buildMetadata({
        locale,
        paths: detailPaths("services", item.seo.alternates),
        seo: item.seo,
        title: item.title ?? t("untranslated"),
        description: item.short_text,
        noindex: !item.is_translated,
    });
}
export default async function ServicePage({ params }: Props) {
    const { locale, slug: rawSlug } = await params;
    const slug = decodeURIComponent(rawSlug);
    setRequestLocale(locale);
    const [item, t, nav] = await Promise.all([
        getService(locale, slug),
        getTranslations("Services"),
        getTranslations("Nav"),
    ]);
    if (!item) notFound();
    redirectToOwnSlug(locale, "services", slug, item);
    const title = item.title ?? t("untranslated");
    const hasContact =
        item.contact_person || item.contact_phone || item.contact_email;
    return (
        <>
            <SetAlternates section="services" slugs={item.seo.alternates} />
            <PageHeader
                title={title}
                lead={item.short_text ?? undefined}
                breadcrumbs={[
                    { label: nav("services"), href: "/services" },
                    { label: title },
                ]}
            />
            {item.is_translated ? (
                <div className="container-page space-y-10 py-12">
                    {item.content && <RichText html={item.content} />}
                    {item.how_to_apply && (
                        <section>
                            <SectionTitle>{t("steps")}</SectionTitle>
                            <p className="whitespace-pre-line">
                                {item.how_to_apply}
                            </p>
                        </section>
                    )}
                    {hasContact && (
                        <section>
                            <SectionTitle>{t("contactPerson")}</SectionTitle>
                            {item.contact_person && (
                                <p className="font-semibold">
                                    {item.contact_person}
                                </p>
                            )}
                            {item.contact_phone && (
                                <a
                                    className="block text-primary"
                                    href={`tel:${item.contact_phone.replace(/[^+\d]/g, "")}`}
                                >
                                    {item.contact_phone}
                                </a>
                            )}
                            {item.contact_email && (
                                <a
                                    className="block text-primary"
                                    href={`mailto:${item.contact_email}`}
                                >
                                    {item.contact_email}
                                </a>
                            )}
                        </section>
                    )}
                    <Button
                        href={`/contacts?subject=${encodeURIComponent(title)}#form`}
                    >
                        {t("apply")}
                    </Button>
                </div>
            ) : (
                <div className="container-page py-12">
                    <p className="text-muted">{t("untranslated")}</p>
                </div>
            )}
            <CtaBlock />
        </>
    );
}
