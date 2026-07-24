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
        'dashboard/payments',
        'dashboard/item',
        'dashboard/day-book',
        'settings/sales-view-settings',
        'settings/payment-view-settings',
      ],
    },
    {
      type: 'category',
      label: 'Sales',
      items: [
        'sales/overview',
        'grow/overview',
        'campaigns/overview',
        'ai-agent/overview',
        'customers/overview',
        'products/overview',
        'orders/overview',
        'invoices/overview',
        'payments/overview',
        'ledger/overview',
        'field-ops/overview',
        'schemes/overview',
        'price-list/overview',
        'forms/overview',
      ],
    },
    {
      type: 'category',
      label: 'Reports',
      items: [
        'customer-analysis/overview',
        'product-analysis/overview',
        'sales-team-activity/overview',
        'sales-team-clockin-report/overview',
        'checkins/overview',
        'order-report/overview',
        'order-items-report/overview',
        'invoice-report/overview',
        'payment-report/overview',
        'supply-tracker/overview',
        'dynamic-segments/overview',
        'scheme-report/overview',
        'trial-balance/overview',
      ],
    },
    {
      type: 'category',
      label: 'Threads',
      items: [
        'threads/overview',
        'threads/query-types',
        'queries/overview',
      ],
    },
    {
      type: 'category',
      label: 'Account Settings',
      items: [
        'account/overview',
        'my-team/overview',
        'department/overview',
        'notification/overview',
        'bank-details/overview',
      ],
    },
    {
      type: 'category',
      label: 'WhatsApp & Communication',
      items: [
        'whatsapp/overview',
        'chat-widget/overview',
      ],
    },
    {
      type: 'category',
      label: 'Integrations & Data',
      items: [
        'apps/overview',
        'cfa/overview',
        'divisions/overview',
        'file-manager/overview',
        'jobs/overview',
      ],
    },
    {
      type: 'category',
      label: 'Configuration',
      items: [
        'config-settings/overview',
      ],
    },
  ],
};

export default sidebars;
