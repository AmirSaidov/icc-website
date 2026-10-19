import {API_URL} from '@/lib/api';

// Карту сайта строит бэк (ссылки уже ведут на фронт, FRONTEND_URL), отдаём её с домена сайта.
// Не при сборке (бэк на Vercel может быть недоступен), ответ бэка кэшируется на час.
export const dynamic = 'force-dynamic';

export async function GET() {
  const res = await fetch(`${new URL(API_URL).origin}/sitemap.xml`, {next: {revalidate: 3600}}).catch(() => null);
  if (!res?.ok) return new Response('Sitemap unavailable', {status: 503});
  return new Response(await res.text(), {
    headers: {'Content-Type': 'application/xml; charset=utf-8'}
  });
}
