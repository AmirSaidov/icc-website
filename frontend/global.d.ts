import type {routing} from '@/i18n/routing';
import type messages from './messages/ru.json';

// Ключи переводов проверяются TypeScript'ом по ru.json:
// опечатка в t('Nav.abuot') — ошибка компиляции.
declare module 'next-intl' {
  interface AppConfig {
    Locale: (typeof routing.locales)[number];
    Messages: typeof messages;
  }
}
