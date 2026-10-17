import {NextResponse} from 'next/server';
import {API_LANG, API_URL, USE_MOCKS} from '@/lib/api';
import type {FeedbackPayload} from '@/lib/api-types';
import {routing, type Locale} from '@/i18n/routing';

/**
 * Прокси POST /feedback/ → Django. Браузер ходит на свой домен:
 * не нужен CORS и адрес бэка не светится в клиенте.
 * IP клиента передаём в X-Forwarded-For — по нему бэк считает лимит (429).
 */
export async function POST(request: Request) {
  const body = (await request.json().catch(() => null)) as FeedbackPayload | null;
  if (!body || typeof body !== 'object') {
    return NextResponse.json({non_field_errors: ['Invalid JSON']}, {status: 400});
  }
  const locale: Locale = routing.locales.includes(body.locale) ? body.locale : routing.defaultLocale;

  if (USE_MOCKS) return mockFeedback(body);

  const forwardedFor = request.headers.get('x-forwarded-for') ?? request.headers.get('x-real-ip') ?? '';
  const res = await fetch(`${API_URL}/feedback/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      'Accept-Language': API_LANG[locale],
      ...(forwardedFor && {'X-Forwarded-For': forwardedFor})
    },
    body: JSON.stringify(body),
    cache: 'no-store'
  });
  const data = await res.json().catch(() => ({}));
  return NextResponse.json(data, {status: res.status});
}

/**
 * Моки для проверки формы без бэка:
 * - email на @example.invalid → 400 с ошибкой под полем;
 * - тема «429» → «слишком много запросов»;
 * - иначе 201.
 */
async function mockFeedback(body: FeedbackPayload) {
  await new Promise((resolve) => setTimeout(resolve, 700));
  if (body.email?.endsWith('@example.invalid')) {
    return NextResponse.json({email: ['Mock: этот адрес не принимается.']}, {status: 400});
  }
  if (body.subject === '429') {
    return NextResponse.json({detail: 'Mock: throttled'}, {status: 429});
  }
  return NextResponse.json({id: Date.now()}, {status: 201});
}
