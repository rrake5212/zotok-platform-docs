import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  docsSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/login',
      ],
    },
    {
      type: 'category',
      label: 'Dashboard',
      items: [
        'dashboard/overview',
        'dashboard/kpi-cards',
        'dashboard/customer-table',
      ],
    },
    {
      type: 'category',
      label: 'Sales',
      items: [
        'sales/overview',
      ],
    },
    {
      type: 'category',
      label: 'Payments',
      items: [
        'payments/overview',
      ],
    },
    {
      type: 'category',
      label: 'Products',
      items: [
        'products/overview',
      ],
    },
    {
      type: 'category',
      label: 'Threads',
      items: [
        'threads/overview',
        'threads/query-types',
      ],
    },
    {
      type: 'category',
      label: 'Queries Management',
      items: [
        'queries/overview',
      ],
    },
    {
      type: 'category',
      label: 'Campaigns (Grow)',
      items: [
        'campaigns/overview',
        'campaigns/customer-lifecycle',
        'campaigns/creating-campaign',
        'campaigns/templates',
      ],
    },
    {
      type: 'category',
      label: 'Settings & Configuration',
      items: [
        'settings/sales-view-settings',
        'settings/payment-view-settings',
      ],
    },
    {
      type: 'category',
      label: 'Additional Modules',
      items: [
        'customers/overview',
        'orders/overview',
        'invoices/overview',
        'ledger/overview',
        'schemes/overview',
        'price-list/overview',
        'field-ops/overview',
        'forms/overview',
        'day-book/overview',
      ],
    },
  ],
};

export default sidebars;
