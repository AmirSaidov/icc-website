export default function Loading() {
    return (
        <main className="container-page space-y-8 py-12" aria-hidden="true">
            <div className="h-10 w-2/3 animate-pulse rounded bg-primary-light" />
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {Array.from({ length: 6 }, (_, i) => (
                    <div
                        key={i}
                        className="overflow-hidden rounded-lg border border-border"
                    >
                        <div className="aspect-[3/2] animate-pulse bg-primary-light" />
                        <div className="space-y-3 p-5">
                            <div className="h-5 animate-pulse rounded bg-primary-light" />
                            <div className="h-4 w-4/5 animate-pulse rounded bg-primary-light" />
                        </div>
                    </div>
                ))}
            </div>
        </main>
    );
}
