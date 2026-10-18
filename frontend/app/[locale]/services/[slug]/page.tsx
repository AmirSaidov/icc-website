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
import { buildMetadata, detailPaths } from "@/lib/seo";
export const revalidate = 60;
type Props = { params: Promise<{ locale: Locale; slug: string }> };
export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { locale, slug } = await params;
    const item = await getService(locale, decodeURIComponent(slug));
    if (!item) return {};
    return buildMetadata({
        locale,
        paths: detailPaths("services", item.seo.alternates),
        seo: item.seo,
        title: item.title,
        description: item.summary,
        noindex: !item.is_translated,
    });
}
export default async function ServicePage({ params }: Props) {
    const { locale, slug } = await params;
    setRequestLocale(locale);
    const [item, t, nav] = await Promise.all([
        getService(locale, decodeURIComponent(slug)),
        getTranslations("Services"),
        getTranslations("Nav"),
    ]);
    if (!item) notFound();
    return (
        <>
            <SetAlternates section="services" slugs={item.seo.alternates} />
            <PageHeader
                title={item.title}
                lead={item.summary}
                breadcrumbs={[
                    { label: nav("services"), href: "/services" },
                    { label: item.title },
                ]}
            />
            {item.is_translated ? (
                <main className="container-page space-y-10 py-12">
                    <RichText html={item.content} />
                    {item.steps.length > 0 && (
                        <section>
                            <SectionTitle>{t("steps")}</SectionTitle>
                            <ol className="list-decimal space-y-4 pl-6">
                                {item.steps.map((step, i) => (
                                    <li key={`${step.title}-${i}`}>
                                        <h3 className="font-semibold">
                                            {step.title}
                                        </h3>
                                        <p className="text-muted">
                                            {step.text}
                                        </p>
                                    </li>
                                ))}
                            </ol>
                        </section>
                    )}
                    {item.contact_person && (
                        <section>
                            <SectionTitle>{t("contactPerson")}</SectionTitle>
                            <p className="font-semibold">
                                {item.contact_person.name}
                            </p>
                            <p className="text-muted">
                                {item.contact_person.position}
                            </p>
                            <a
                                className="text-primary"
                                href={`tel:${item.contact_person.phone}`}
                            >
                                {item.contact_person.phone}
                            </a>
                            <br />
                            <a
                                className="text-primary"
                                href={`mailto:${item.contact_person.email}`}
                            >
                                {item.contact_person.email}
                            </a>
                        </section>
                    )}
                    <Button
                        href={`/contacts?subject=${encodeURIComponent(item.title)}#form`}
                    >
                        {t("apply")}
                    </Button>
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
