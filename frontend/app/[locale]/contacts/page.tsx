import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { PageHeader } from "@/components/ui/PageHeader";
import { SectionTitle } from "@/components/ui/SectionTitle";
import { FeedbackForm } from "@/components/ui/FeedbackForm";
import { getContacts } from "@/lib/api";
import { buildMetadata, staticPaths } from "@/lib/seo";
import type { Locale } from "@/i18n/routing";
export const revalidate = 60;
// Читает searchParams (?subject= из «Подать заявку» на услуге) — рендерится на каждый запрос; ответы API всё равно кэшируются на 60 с.
export const dynamic = "force-dynamic";
type Props = {
    params: Promise<{ locale: Locale }>;
    searchParams: Promise<{ subject?: string }>;
};
export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { locale } = await params;
    const t = await getTranslations({ locale, namespace: "Contacts" });
    return buildMetadata({
        locale,
        paths: staticPaths("/contacts"),
        title: t("title"),
        description: t("description"),
    });
}
export default async function ContactsPage({ params, searchParams }: Props) {
    const { locale } = await params;
    const { subject = "" } = await searchParams;
    setRequestLocale(locale);
    const [data, t, nav] = await Promise.all([
        getContacts(locale),
        getTranslations("Contacts"),
        getTranslations("Nav"),
    ]);
    // Встраиваемая карта OpenStreetMap (без ключа) + ссылка на ту же точку в 2ГИС.
    const point =
        data.map_lat != null && data.map_lng != null
            ? { lat: data.map_lat, lng: data.map_lng }
            : null;
    const map = point && {
        embed: `https://www.openstreetmap.org/export/embed.html?bbox=${point.lng - 0.006}%2C${point.lat - 0.003}%2C${point.lng + 0.006}%2C${point.lat + 0.003}&layer=mapnik&marker=${point.lat}%2C${point.lng}`,
        twoGis: `https://2gis.kg/bishkek/geo/${point.lng}%2C${point.lat}?m=${point.lng}%2C${point.lat}%2F17`,
    };
    return (
        <>
            <PageHeader
                title={t("title")}
                breadcrumbs={[{ label: nav("contacts") }]}
            />
            <div className="container-page grid min-w-0 gap-12 py-12 lg:grid-cols-2">
                <section className="min-w-0">
                    <SectionTitle>{t("organization")}</SectionTitle>
                    {data.official_name && (
                        <p className="text-lg font-semibold">{data.official_name}</p>
                    )}
                    <div className="mt-5 space-y-3 text-muted">
                        {data.address && <p>{data.address}</p>}
                        <ul>
                            {data.phones.map((phone) => (
                                <li key={phone.number}>
                                    {phone.label && `${phone.label}: `}
                                    <a
                                        className="text-primary"
                                        href={`tel:${phone.number.replace(/[^+\d]/g, "")}`}
                                    >
                                        {phone.number}
                                    </a>
                                </li>
                            ))}
                        </ul>
                        {data.email && (
                            <p>
                                <a
                                    className="text-primary"
                                    href={`mailto:${data.email}`}
                                >
                                    {data.email}
                                </a>
                            </p>
                        )}
                        {data.work_hours && (
                            <p>
                                <span className="font-medium text-text">
                                    {t("schedule")}:{" "}
                                </span>
                                {data.work_hours}
                            </p>
                        )}
                    </div>
                    {map && (
                        <div className="mt-8">
                            <div className="overflow-hidden rounded-lg border border-border">
                                <iframe
                                    src={map.embed}
                                    loading="lazy"
                                    title={t("mapTitle")}
                                    className="h-80 w-full border-0"
                                />
                            </div>
                            <a
                                href={map.twoGis}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="mt-3 inline-block text-sm font-medium text-primary hover:underline"
                            >
                                {t("openIn2gis")}
                            </a>
                        </div>
                    )}
                </section>
                <section id="form" className="min-w-0 scroll-mt-24">
                    <SectionTitle>{t("formTitle")}</SectionTitle>
                    <FeedbackForm type="contact" defaultSubject={subject} />
                </section>
            </div>
        </>
    );
}
