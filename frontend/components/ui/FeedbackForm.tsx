'use client';

import {useState} from 'react';
import {useLocale, useTranslations} from 'next-intl';
import {zodResolver} from '@hookform/resolvers/zod';
import {useForm} from 'react-hook-form';
import {z} from 'zod';
import type {Locale} from '@/i18n/routing';
import type {FeedbackType} from '@/lib/api-types';
import {sendFeedback} from '@/lib/feedback';
import {cn} from '@/lib/cn';
import {Button} from './Button';

/** Те же правила, что у бэка (backend/SPEC.md, 5.1). */
const schema = z.object({
  full_name: z.string().trim().min(2).max(150),
  company: z.string().trim().min(1).max(200),
  country: z.string().trim().min(1).max(100),
  email: z.string().trim().pipe(z.email()),
  phone: z.string().trim().max(30).regex(/^[+\d\s()-]*$/),
  subject: z.string().trim().min(1).max(200),
  message: z.string().trim().min(10).max(5000),
  consent: z.boolean().refine(Boolean),
  website: z.string()
});

type Values = z.infer<typeof schema>;

const FIELDS = [
  {name: 'full_name', required: true, autoComplete: 'name'},
  {name: 'company', required: true, autoComplete: 'organization'},
  {name: 'country', required: true, autoComplete: 'country-name'},
  {name: 'email', required: true, autoComplete: 'email', type: 'email'},
  {name: 'phone', required: false, autoComplete: 'tel', type: 'tel'},
  {name: 'subject', required: true},
  {name: 'message', required: true}
] as const;

const control = 'w-full min-w-0 rounded-md border bg-white px-3 py-2 text-text';

export function FeedbackForm({type, defaultSubject = ''}: {type: FeedbackType; defaultSubject?: string}) {
  const t = useTranslations('Feedback');
  const locale = useLocale() as Locale;
  const [success, setSuccess] = useState(false);
  const {
    register,
    handleSubmit,
    setError,
    formState: {errors, isSubmitting}
  } = useForm<Values>({
    resolver: zodResolver(schema),
    defaultValues: {
      full_name: '',
      company: '',
      country: '',
      email: '',
      phone: '',
      subject: defaultSubject,
      message: '',
      consent: false,
      website: ''
    }
  });

  const submit = async (values: Values) => {
    const result = await sendFeedback({...values, phone: values.phone || null, type, lang: locale});
    if (result.ok) {
      setSuccess(true);
      return;
    }
    if (result.status === 429) {
      setError('root', {message: t('tooMany')});
      return;
    }
    if (result.status === 400 && 'errors' in result) {
      // Сообщения бэка всегда на русском — под полем показываем свой текст на языке сайта.
      const fields = Object.keys(result.errors).filter((field): field is keyof Values => field in values);
      fields.forEach((field, index) => setError(field, {type: 'server'}, {shouldFocus: index === 0}));
      // Ошибка не по полю формы (non_field_errors, detail, type, lang) — иначе человек не увидит ничего.
      if (fields.length) return;
    }
    setError('root', {message: t('error')});
  };

  if (success) {
    return (
      <p role="status" className="rounded-lg bg-primary-light p-6 text-text">
        {t('success')}
      </p>
    );
  }

  return (
    <form onSubmit={handleSubmit(submit)} className="relative grid min-w-0 gap-5 sm:grid-cols-2" noValidate>
      {FIELDS.map((field) => {
        const {name, required} = field;
        const error = errors[name];
        const errorId = `${name}-error`;
        const common = {
          id: name,
          'aria-invalid': error ? true : undefined,
          'aria-describedby': error ? errorId : undefined,
          'aria-required': required || undefined,
          className: cn(control, error ? 'border-danger' : 'border-border'),
          ...register(name)
        };
        return (
          <div key={name} className={cn('min-w-0', name === 'message' && 'sm:col-span-2')}>
            <label htmlFor={name} className="mb-1 block font-medium">
              {t(`fields.${name}`)}
              {required && ' *'}
            </label>
            {name === 'message' ? (
              <textarea rows={5} {...common} />
            ) : (
              <input type={'type' in field ? field.type : 'text'} autoComplete={'autoComplete' in field ? field.autoComplete : undefined} {...common} />
            )}
            {error && (
              <p id={errorId} className="mt-1 text-sm text-danger">
                {t('invalid')}
              </p>
            )}
          </div>
        );
      })}

      {/* honeypot: не display:none — часть ботов такие поля пропускает; прячем за экран */}
      <div aria-hidden="true" className="absolute -left-[10000px] size-px overflow-hidden">
        <label htmlFor="website">Website</label>
        <input id="website" type="text" tabIndex={-1} autoComplete="off" {...register('website')} />
      </div>

      <div className="sm:col-span-2">
        <label className="flex items-start gap-3">
          <input
            type="checkbox"
            className="mt-1"
            aria-invalid={errors.consent ? true : undefined}
            aria-describedby={errors.consent ? 'consent-error' : undefined}
            {...register('consent')}
          />
          <span>{t('consent')}</span>
        </label>
        {errors.consent && (
          <p id="consent-error" className="mt-1 text-sm text-danger">
            {t('required')}
          </p>
        )}
      </div>

      <div className="sm:col-span-2">
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? t('sending') : t('submit')}
        </Button>
        {errors.root && (
          <p role="alert" className="mt-2 text-sm text-danger">
            {errors.root.message}
          </p>
        )}
      </div>
    </form>
  );
}
