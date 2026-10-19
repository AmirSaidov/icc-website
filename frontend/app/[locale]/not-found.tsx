import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
export default async function NotFound() {
    const t = await getTranslations("Errors");
    return (
        <div className="container-page py-20 text-center">
            <p className="text-7xl font-bold text-primary">404</p>
            <h1 className="mt-4 text-3xl font-bold">{t("notFoundTitle")}</h1>
            <p className="mt-3 text-muted">{t("notFound")}</p>
            <Link
                href="/"
                className="mt-8 inline-flex rounded-md bg-primary px-5 py-3 text-white"
            >
                {t("home")}
            </Link>
        </div>
    );
}
