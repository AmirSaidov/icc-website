import type {NextConfig} from 'next';
import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin('./i18n/request.ts');

// Без API_URL на Vercel сайт ходил бы в 127.0.0.1 — лучше сразу уронить сборку с понятной ошибкой.
if (process.env.VERCEL && !process.env.API_URL) {
  throw new Error('API_URL не задан: Vercel → Settings → Environment Variables, например https://<логин>.pythonanywhere.com/api/v1');
}

// Картинки и файлы Django отдаёт с того же хоста, что и API (/media/...).
const apiUrl = new URL(process.env.API_URL ?? 'http://127.0.0.1:8000/api/v1');

const nextConfig: NextConfig = {
  images: {
    // Оба протокола: схему в абсолютных URL Django берёт из X-Forwarded-Proto прокси хостинга.
    remotePatterns: (['https', 'http'] as const).map((protocol) => ({
      protocol,
      hostname: apiUrl.hostname,
      port: apiUrl.port,
      pathname: '/media/**'
    }))
  }
};

export default withNextIntl(nextConfig);
