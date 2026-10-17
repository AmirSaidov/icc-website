import {
  BadgeCheck,
  ChartColumn,
  Circle,
  Cog,
  Factory,
  Handshake,
  Landmark,
  Languages,
  MessagesSquare,
  Plane,
  Presentation,
  Search,
  Shield,
  Truck,
  type LucideIcon,
  type LucideProps
} from 'lucide-react';

/**
 * Иконки, имена которых приходят из API (направления, услуги, преимущества).
 * Новое имя в админке → добавить сюда. Неизвестное имя → нейтральный кружок.
 */
const ICONS: Record<string, LucideIcon> = {
  'badge-check': BadgeCheck,
  chart: ChartColumn,
  cog: Cog,
  factory: Factory,
  handshake: Handshake,
  landmark: Landmark,
  languages: Languages,
  messages: MessagesSquare,
  plane: Plane,
  presentation: Presentation,
  search: Search,
  shield: Shield,
  truck: Truck
};

export function Icon({name, ...props}: {name: string} & LucideProps) {
  const Component = ICONS[name] ?? Circle;
  return <Component aria-hidden strokeWidth={1.75} {...props} />;
}
