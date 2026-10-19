import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { DirectionCard } from "@/components/ui/DirectionCard";
import { PageHeader } from "@/components/ui/PageHeader";
import { Link } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";
import { getDirections } from "@/lib/api";
import { buildMetadata, staticPaths } from "@/lib/seo";

export const revalidate = 60;
type Props = { params: Promise<{ locale: Locale }> };
export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { locale } = await params;
    const t = await getTranslations({ locale, namespace: "Directions" });
    return buildMetadata({
        locale,
        paths: staticPaths("/directions"),
        title: t("title"),
        description: t("description"),
    });
}
export default async function DirectionsPage({ params }: Props) {
    const { locale } = await params;
    setRequestLocale(locale);
    const [items, t, nav] = await Promise.all([
        getDirections(locale),
        getTranslations("Directions"),
        getTranslations("Nav"),
    ]);
    return (
        <>
            <PageHeader
                title={t("title")}
                lead={t("description")}
                breadcrumbs={[{ label: nav("directions") }]}
            />
            <section className="container-page py-12">
                <ul data-reveal-stagger className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    {items.map((item) => (
                        <li key={item.id} className="flex [&>*]:flex-1">
                            <DirectionCard item={item} />
                        </li>
                    ))}
                </ul>
                {!items.length && <p className="text-muted">{t("empty")}</p>}
                <Link
                    href="/services"
                    className="mt-8 inline-block text-primary underline"
                >
                    {t("services")}
                </Link>
            </section>
        </>
    );
}
