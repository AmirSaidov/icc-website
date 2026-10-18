import {NextResponse} from 'next/server';
import {API_URL} from '@/lib/api';
import type {FeedbackPayload} from '@/lib/api-types';

/**
 * Прокси POST /feedback/ → Django. Браузер ходит на свой домен:
 * не нужен CORS и адрес бэка не светится в клиенте.
 * IP клиента передаём в X-Forwarded-For — по нему бэк считает лимит (429).
 * На Vercel x-forwarded-for выставляет сам Vercel, клиент его не подделает.
 */
export async function POST(request: Request) {
  const body = (await request.json().catch(() => null)) as FeedbackPayload | null;
  if (!body || typeof body !== 'object') {
    return NextResponse.json({non_field_errors: ['Invalid JSON']}, {status: 400});
  }

  const forwardedFor = request.headers.get('x-forwarded-for') ?? request.headers.get('x-real-ip') ?? '';
  let res: Response;
  try {
    res = await fetch(`${API_URL}/feedback/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        ...(forwardedFor && {'X-Forwarded-For': forwardedFor})
      },
      body: JSON.stringify(body),
      cache: 'no-store'
    });
  } catch (error) {
    console.error('[feedback] backend unreachable:', error);
    return NextResponse.json({detail: 'Backend unavailable'}, {status: 502});
  }
  const data = await res.json().catch(() => ({}));
  return NextResponse.json(data, {status: res.status});
}
