import {
  FileCode2,
  Braces,
  Database,
  Atom,
  GitBranch,
  Code,
  LucideIcon,
} from 'lucide-react';

// Map of icon names to components
const iconMap: Record<string, LucideIcon> = {
  FileCode2,
  Braces,
  Database,
  Atom,
  GitBranch,
  Code,
};

interface DynamicIconProps {
  name: string;
  className?: string;
  style?: React.CSSProperties;
}

export default function DynamicIcon({ name, className, style }: DynamicIconProps) {
  const IconComponent = iconMap[name] || Code;
  return <IconComponent className={className} style={style} />;
}
