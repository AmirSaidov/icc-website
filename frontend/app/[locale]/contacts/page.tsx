import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { PageHeader } from "@/components/ui/PageHeader";
import { SectionTitle } from "@/components/ui/SectionTitle";
import { FeedbackForm } from "@/components/ui/FeedbackForm";
import { getContacts } from "@/lib/api";
import { buildMetadata, staticPaths } from "@/lib/seo";
import type { Locale } from "@/i18n/routing";
export const revalidate = 60;
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
    const map = `https://maps.2gis.com/widget?m=${data.map_lng}%2C${data.map_lat}%2F16`;
    return (
        <>
            <PageHeader
                title={t("title")}
                breadcrumbs={[{ label: nav("contacts") }]}
            />
            <main className="container-page grid min-w-0 gap-12 py-12 lg:grid-cols-2">
                <section className="min-w-0">
                    <SectionTitle>{t("organization")}</SectionTitle>
                    <h2 className="text-lg font-semibold">{data.name}</h2>
                    <div className="mt-5 space-y-3 text-muted">
                        <p>{data.address}</p>
                        <ul>
                            {data.phones.map((phone) => (
                                <li key={phone}>
                                    <a
                                        className="text-primary"
                                        href={`tel:${phone.replace(/[^+\d]/g, "")}`}
                                    >
                                        {phone}
                                    </a>
                                </li>
                            ))}
                        </ul>
                        <ul>
                            {data.emails.map((email) => (
                                <li key={email}>
                                    <a
                                        className="text-primary"
                                        href={`mailto:${email}`}
                                    >
                                        {email}
                                    </a>
                                </li>
                            ))}
                        </ul>
                        {data.schedule && (
                            <p>
                                <span className="font-medium text-text">
                                    {t("schedule")}:{" "}
                                </span>
                                {data.schedule}
                            </p>
                        )}
                    </div>
                    <div className="mt-8 overflow-hidden rounded-lg border border-border">
                        <iframe
                            src={map}
                            loading="lazy"
                            title={t("mapTitle")}
                            className="h-80 w-full border-0"
                            referrerPolicy="no-referrer-when-downgrade"
                        />
                    </div>
                </section>
                <section id="form" className="min-w-0 scroll-mt-24">
                    <SectionTitle>{t("formTitle")}</SectionTitle>
                    <FeedbackForm type="contact" defaultSubject={subject} />
                </section>
            </main>
        </>
    );
}
