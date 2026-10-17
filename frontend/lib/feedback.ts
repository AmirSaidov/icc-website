import type {FeedbackPayload, FieldErrors} from './api-types';

export type FeedbackResult =
  | {ok: true}
  | {ok: false; status: 400; errors: FieldErrors}
  | {ok: false; status: 429}
  | {ok: false; status: number};

/**
 * Отправка формы обратной связи из браузера (FeedbackForm).
 * Идёт через app/api/feedback → POST /feedback/ на бэке.
 *
 *   const result = await sendFeedback(values);
 *   if (!result.ok && result.status === 400) — ошибки под полями из result.errors
 *   if (!result.ok && result.status === 429) — «Слишком много запросов…»
 */
export async function sendFeedback(payload: FeedbackPayload): Promise<FeedbackResult> {
  let res: Response;
  try {
    res = await fetch('/api/feedback', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
  } catch {
    return {ok: false, status: 0};
  }
  if (res.ok) return {ok: true};
  if (res.status === 400) {
    const errors = (await res.json().catch(() => ({}))) as FieldErrors;
    return {ok: false, status: 400, errors};
  }
  return {ok: false, status: res.status};
}
