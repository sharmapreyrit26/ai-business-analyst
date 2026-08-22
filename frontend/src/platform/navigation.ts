import {
  Activity,
  BarChart3,
  Bot,
  Boxes,
  Database,
  FileSearch,
  Gauge,
  GitCompareArrows,
  Megaphone,
  PackageSearch,
  Settings,
  ShieldCheck,
  ShoppingBag,
  SlidersHorizontal,
  Truck,
  Users,
  WalletCards,
} from 'lucide-react'

export const navigation = [
  {
    section: 'Overview',
    items: [
      {
        label: 'Business Health',
        path: '/',
        icon: Gauge,
      },
      {
        label: 'Revenue & Profit',
        path: '/revenue-profit',
        icon: WalletCards,
      },
    ],
  },

  {
    section: 'Analytics',
    items: [
      {
        label: 'Marketing',
        path: '/marketing',
        icon: Megaphone,
      },
      {
        label: 'Products',
        path: '/products',
        icon: ShoppingBag,
      },
      {
        label: 'Customers',
        path: '/customers',
        icon: Users,
      },
      {
        label: 'Logistics',
        path: '/logistics',
        icon: Truck,
      },
      {
        label: 'Inventory',
        path: '/inventory',
        icon: Boxes,
      },
    ],
  },

  {
    section: 'Intelligence',
    items: [
      {
        label: 'AI Analyst',
        path: '/analyst',
        icon: Bot,
      },
      {
        label: 'Investigations',
        path: '/investigations',
        icon: FileSearch,
      },
      {
        label: 'Scenario Lab',
        path: '/scenario',
        icon: SlidersHorizontal,
      },
    ],
  },

  {
    section: 'Data',
    items: [
      {
        label: 'Data Sources',
        path: '/data-sources',
        icon: Database,
      },
      {
        label: 'Data Quality',
        path: '/data-quality',
        icon: ShieldCheck,
      },
      {
        label: 'Data Explorer',
        path: '/data-explorer',
        icon: BarChart3,
      },
    ],
  },

  {
    section: 'System',
    items: [
      {
        label: 'Metric Dictionary',
        path: '/metrics',
        icon: GitCompareArrows,
      },
      {
        label: 'Settings',
        path: '/settings',
        icon: Settings,
      },
    ],
  },
] as const
