/**
 * Navigation sidebar configuration
 * Converted from Docusaurus sidebars.ts
 */

const sidebarConfig = [
  { type: 'doc', id: 'intro', label: 'Introduction' },
  {
    type: 'category',
    label: 'Getting Started',
    items: ['getting-started/login'],
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
    ],
  },
  {
    type: 'category',
    label: 'Sales',
    items: [
      'grow/overview',
      'campaigns/overview',
      'campaigns/creating-campaign',
      'campaigns/customer-lifecycle',
      'campaigns/templates',
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
    items: ['threads/overview', 'threads/query-types'],
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
    items: ['whatsapp/overview', 'chat-widget/overview'],
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
    items: ['config-settings/overview'],
  },
];

export function flattenSidebar() {
  const flat = [];
  function walk(items) {
    for (const item of items) {
      if (item.type === 'doc') {
        flat.push({ id: item.id, label: item.label });
      } else if (item.type === 'category') {
        for (const childId of item.items) {
          const label = childId.split('/').pop().replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
          flat.push({ id: childId, label, category: item.label });
        }
      }
    }
  }
  walk(sidebarConfig);
  return flat;
}

export default sidebarConfig;
