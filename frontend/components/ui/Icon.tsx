import {
  BadgeCheck,
  ChartColumn,
  Circle,
  Cog,
  Factory,
  Handshake,
  Landmark,
  Languages,
  MapPin,
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
 * Иконки, имена которых приходят из API (направления — поле icon, см. IconEnum в схеме).
 * Новое имя в админке → добавить сюда. Неизвестное имя → нейтральный кружок.
 */
const ICONS: Record<string, LucideIcon> = {
  // Ключи направлений с бэка
  cooperation: Factory,
  partnership: Handshake,
  'joint-production': Cog,
  localization: MapPin,
  subcontracting: Truck,
  consulting: MessagesSquare,
  'b2b-meetings': Presentation,
  export: Plane,
  // Общие
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
