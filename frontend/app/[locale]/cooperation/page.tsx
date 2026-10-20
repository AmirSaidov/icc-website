import type { Metadata } from "next";
import Image from "next/image";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { PageHeader } from "@/components/ui/PageHeader";
import { SectionTitle } from "@/components/ui/SectionTitle";
import { FeedbackForm } from "@/components/ui/FeedbackForm";
import { CardLink } from "@/components/ui/Card";
import { PartnerCard } from "@/components/ui/PartnerCard";
import { FilterSelect } from "@/components/ui/FilterSelect";
import { CARD_IMAGE_SIZES } from "@/components/ui/NewsCard";
import { getCountries, getPartners, getProjects, getPage } from "@/lib/api";
import { buildMetadata, staticPaths } from "@/lib/seo";
import { RichText } from "@/components/ui/RichText";
import type { Locale } from "@/i18n/routing";
export const revalidate = 60;
// Читает searchParams (фильтры) — рендерится на каждый запрос; ответы API всё равно кэшируются на 60 с.
export const dynamic = "force-dynamic";
type Props = {
    params: Promise<{ locale: Locale }>;
    searchParams: Promise<{ country?: string }>;
};
export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { locale } = await params;
    const [page, t] = await Promise.all([
        getPage(locale, "cooperation"),
        getTranslations({ locale, namespace: "Cooperation" }),
    ]);
    return buildMetadata({
        locale,
        paths: staticPaths("/cooperation"),
        seo: page?.seo,
        title: page?.title ?? t("title"),
    });
}
export default async function CooperationPage({ params, searchParams }: Props) {
    const { locale } = await params;
    const { country = "" } = await searchParams;
    setRequestLocale(locale);
    const [page, countries, partners, projects, t, nav] = await Promise.all([
        getPage(locale, "cooperation"),
        getCountries(locale),
        getPartners(locale, country || undefined),
        getProjects(locale, { country: country || undefined, pageSize: 50 }),
        getTranslations("Cooperation"),
        getTranslations("Nav"),
    ]);
    return (
        <>
            <PageHeader
                title={page?.title ?? t("title")}
                breadcrumbs={[{ label: nav("cooperation") }]}
            />
            <div className="container-page space-y-12 py-12">
                {page?.content && (
                    <RichText html={page.content} className="max-w-3xl" />
                )}
                <FilterSelect
                    param="country"
                    label={t("country")}
                    allLabel={t("allCountries")}
                    value={country.toUpperCase()}
                    options={countries.map((c) => ({
                        value: c.code,
                        label: c.name ?? c.code,
                    }))}
                />
                <section>
                    <SectionTitle>{t("partners")}</SectionTitle>
                    <ul data-reveal-stagger className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                        {partners.map((p) => (
                            <li key={p.id} className="min-w-0">
                                <PartnerCard partner={p} />
                            </li>
                        ))}
                    </ul>
                    {!partners.length && (
                        <p className="text-muted">{t("noPartners")}</p>
                    )}
                </section>
                <section>
                    <SectionTitle>{t("projects")}</SectionTitle>
                    <ul data-reveal-stagger className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                        {projects.results.map((p) => (
                            <li key={p.id} className="flex [&>*]:flex-1">
                                <article className="group relative flex flex-col gap-3">
                                    <div className="border border-border bg-surface p-1.5 transition-colors duration-300 group-has-[a.card-link:hover]:border-primary/40">
                                        <div className="relative aspect-[3/2] overflow-hidden bg-primary-light">
                                            {p.cover && (
                                                <Image
                                                    src={p.cover.small}
                                                    alt={p.title ?? ""}
                                                    fill
                                                    sizes={CARD_IMAGE_SIZES}
                                                    className="object-cover transition-transform duration-500 group-has-[a.card-link:hover]:scale-105"
                                                />
                                            )}
                                        </div>
                                    </div>
                                    <div className="flex flex-col gap-1.5">
                                        {p.country.name && (
                                            <p className="text-xs font-semibold text-primary">
                                                {p.country.name}
                                            </p>
                                        )}
                                        <h3 className="text-lg font-bold leading-snug text-navy">
                                            <CardLink
                                                href={`/cooperation/projects/${p.slug}`}
                                            >
                                                {p.title}
                                            </CardLink>
                                        </h3>
                                        {p.excerpt && (
                                            <p className="line-clamp-3 text-sm text-muted">
                                                {p.excerpt}
                                            </p>
                                        )}
                                    </div>
                                </article>
                            </li>
                        ))}
                    </ul>
                    {!projects.results.length && (
                        <p className="text-muted">{t("noProjects")}</p>
                    )}
                </section>
                <section id="form" className="scroll-mt-24">
                    <SectionTitle>{t("formTitle")}</SectionTitle>
                    <FeedbackForm type="cooperation" />
                </section>
            </div>
        </>
    );
}
