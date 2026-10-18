import type { Metadata } from "next";
import Image from "next/image";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { PageHeader } from "@/components/ui/PageHeader";
import { SectionTitle } from "@/components/ui/SectionTitle";
import { FeedbackForm } from "@/components/ui/FeedbackForm";
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
    const page = await getPage(locale, "cooperation");
    if (!page) return {};
    return buildMetadata({
        locale,
        paths: staticPaths("/cooperation"),
        seo: page.seo,
        title: page.title,
        description: page.lead,
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
        getProjects(locale, country || undefined),
        getTranslations("Cooperation"),
        getTranslations("Nav"),
    ]);
    return (
        <>
            <PageHeader
                title={page?.title ?? t("title")}
                lead={page?.lead}
                breadcrumbs={[{ label: nav("cooperation") }]}
            />
            <main className="container-page space-y-12 py-12">
                {page?.content && (
                    <RichText html={page.content} className="max-w-3xl" />
                )}
                <form action="" className="flex flex-wrap items-center gap-3">
                    <label htmlFor="country" className="font-medium">
                        {t("country")}
                    </label>
                    <select
                        id="country"
                        name="country"
                        defaultValue={country}
                        className="min-h-11 max-w-full rounded border border-border bg-white px-3"
                    >
                        <option value="">{t("allCountries")}</option>
                        {countries.map((c) => (
                            <option key={c.id} value={c.code}>
                                {c.name}
                            </option>
                        ))}
                    </select>
                    <button className="rounded bg-primary px-4 py-2 text-white">
                        {t("filter")}
                    </button>
                </form>
                <section>
                    <SectionTitle>{t("partners")}</SectionTitle>
                    <ul className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
                        {partners.map((p) => (
                            <li
                                key={p.id}
                                className="flex min-w-0 items-center justify-center rounded-lg border border-border p-4"
                            >
                                {p.url ? (
                                    <a
                                        href={p.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        aria-label={p.name}
                                    >
                                        <Image
                                            src={p.logo.url}
                                            alt={p.logo.alt || p.name}
                                            width={p.logo.width}
                                            height={p.logo.height}
                                            sizes="(min-width: 1024px) 220px, 40vw"
                                            className="h-auto max-h-24 max-w-full object-contain"
                                        />
                                    </a>
                                ) : (
                                    <Image
                                        src={p.logo.url}
                                        alt={p.logo.alt || p.name}
                                        width={p.logo.width}
                                        height={p.logo.height}
                                        sizes="(min-width: 1024px) 220px, 40vw"
                                        className="h-auto max-h-24 max-w-full object-contain"
                                    />
                                )}
                            </li>
                        ))}
                    </ul>
                    {!partners.length && (
                        <p className="text-muted">{t("noPartners")}</p>
                    )}
                </section>
                <section>
                    <SectionTitle>{t("projects")}</SectionTitle>
                    <ul className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                        {projects.map((p) => (
                            <li
                                key={p.id}
                                className="overflow-hidden rounded-lg border border-border"
                            >
                                {p.cover && (
                                    <div className="relative aspect-[3/2]">
                                        <Image
                                            src={p.cover.url}
                                            alt={p.cover.alt}
                                            fill
                                            sizes="(min-width: 1024px) 33vw, 100vw"
                                            className="object-cover"
                                        />
                                    </div>
                                )}
                                <div className="p-5">
                                    <h3 className="font-semibold">{p.title}</h3>
                                    <p className="mt-2 text-sm text-muted">
                                        {p.summary}
                                    </p>
                                </div>
                            </li>
                        ))}
                    </ul>
                    {!projects.length && (
                        <p className="text-muted">{t("noProjects")}</p>
                    )}
                </section>
                <section id="form" className="scroll-mt-24">
                    <SectionTitle>{t("formTitle")}</SectionTitle>
                    <FeedbackForm type="cooperation" />
                </section>
            </main>
        </>
    );
}
