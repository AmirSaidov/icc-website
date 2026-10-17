import type {NextConfig} from 'next';
import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin('./i18n/request.ts');

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      // Стоковые фото для MVP, заказчик потом заменит.
      {protocol: 'https', hostname: 'images.unsplash.com'},
      // Медиа из Django. Хост прода добавить, когда Айбек его назовёт.
      {protocol: 'http', hostname: 'localhost', port: '8000'},
      {protocol: 'http', hostname: '127.0.0.1', port: '8000'}
    ]
  }
};

export default withNextIntl(nextConfig);
