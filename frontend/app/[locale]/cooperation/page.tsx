import type { Metadata } from "next";
import Image from "next/image";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { PageHeader } from "@/components/ui/PageHeader";
import { SectionTitle } from "@/components/ui/SectionTitle";
import { FeedbackForm } from "@/components/ui/FeedbackForm";
import { Card, CardLink } from "@/components/ui/Card";
import { FilterSelect } from "@/components/ui/FilterSelect";
import { CARD_IMAGE_SIZES } from "@/components/ui/NewsCard";
import { getCountries, getPartners, getProjects, getPage } from "@/lib/api";
import { buildMetadata, staticPaths } from "@/lib/seo";
import { RichText } from "@/components/ui/RichText";
import type { Locale } from "@/i18n/routing";
export const revalidate = 60;
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
                    <ul data-reveal-stagger className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
                        {partners.map((p) => {
                            const logo = p.logo ? (
                                <span className="relative block h-24 w-full">
                                    <Image
                                        src={p.logo.small}
                                        alt={p.name ?? ""}
                                        fill
                                        sizes="(min-width: 1024px) 220px, 40vw"
                                        className="object-contain"
                                    />
                                </span>
                            ) : (
                                <span className="text-center font-medium">
                                    {p.name}
                                </span>
                            );
                            return (
                                <li
                                    key={p.id}
                                    className="flex min-h-32 min-w-0 items-center justify-center rounded-lg border border-border p-4"
                                >
                                    {p.website ? (
                                        <a
                                            href={p.website}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            aria-label={p.name ?? undefined}
                                            className="flex w-full justify-center"
                                        >
                                            {logo}
                                        </a>
                                    ) : (
                                        logo
                                    )}
                                </li>
                            );
                        })}
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
                                <Card>
                                    <div className="relative aspect-[3/2] bg-primary-light">
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
                                    <div className="flex flex-1 flex-col gap-2 p-5">
                                        {p.country.name && (
                                            <span className="text-sm text-muted">
                                                {p.country.name}
                                            </span>
                                        )}
                                        <h3 className="font-semibold">
                                            <CardLink
                                                href={`/cooperation/projects/${p.slug}`}
                                            >
                                                {p.title}
                                            </CardLink>
                                        </h3>
                                        {p.excerpt && (
                                            <p className="text-sm text-muted">
                                                {p.excerpt}
                                            </p>
                                        )}
                                    </div>
                                </Card>
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
