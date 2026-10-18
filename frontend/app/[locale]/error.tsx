"use client";
import { useEffect } from "react";
import { useTranslations } from "next-intl";
export default function ErrorPage({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    const t = useTranslations("Errors");
    useEffect(() => {
        console.error(error);
    }, [error]);
    return (
        <main className="container-page py-20 text-center">
            <h1 className="text-3xl font-bold">{t("errorTitle")}</h1>
            <p className="mt-3 text-muted">{t("errorText")}</p>
            <button
                type="button"
                onClick={reset}
                className="mt-8 rounded-md bg-primary px-5 py-3 text-white"
            >
                {t("retry")}
            </button>
        </main>
    );
}
