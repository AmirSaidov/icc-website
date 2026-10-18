import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { PageHeader } from "@/components/ui/PageHeader";
import { NewsList } from "@/components/ui/NewsList";
import { getNews, getNewsCategories } from "@/lib/api";
import { buildMetadata, staticPaths } from "@/lib/seo";
import type { Locale } from "@/i18n/routing";
export const revalidate = 60;
// Читает searchParams (фильтры) — рендерится на каждый запрос; ответы API всё равно кэшируются на 60 с.
export const dynamic = "force-dynamic";
type Props = {
    params: Promise<{ locale: Locale }>;
    searchParams: Promise<{ category?: string }>;
};
export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { locale } = await params;
    const t = await getTranslations({ locale, namespace: "News" });
    return buildMetadata({
        locale,
        paths: staticPaths("/news"),
        title: t("title"),
        description: t("description"),
    });
}
export default async function NewsPage({ params, searchParams }: Props) {
    const { locale } = await params;
    const { category = "" } = await searchParams;
    setRequestLocale(locale);
    const [data, categories, t, nav] = await Promise.all([
        getNews(locale, { category: category || undefined }),
        getNewsCategories(locale),
        getTranslations("News"),
        getTranslations("Nav"),
    ]);
    return (
        <>
            <PageHeader
                title={t("title")}
                lead={t("description")}
                breadcrumbs={[{ label: nav("news") }]}
            />
            <div className="container-page py-12">
                <NewsList
                    key={category}
                    initial={data.results}
                    categories={categories}
                    category={category}
                    hasMore={Boolean(data.next)}
                />
            </div>
        </>
    );
}
