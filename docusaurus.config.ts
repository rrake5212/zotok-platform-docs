import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'ZoTok Platform Manual',
  tagline: 'Field Operations & Distributor Management Platform',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  url: 'https://rrake5212.github.io',
  baseUrl: '/zotok-platform-docs/',

  organizationName: 'rrake5212',
  projectName: 'zotok-platform-docs',

  onBrokenLinks: 'throw',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'throw',
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl: undefined,
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/logo.svg',
    colorMode: {
      respectPrefersColorScheme: true,
      defaultMode: 'light',
    },
    navbar: {
      title: 'ZoTok Platform Manual',
      logo: {
        alt: 'ZoTok Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docsSidebar',
          label: 'Documentation',
          position: 'left',
        },
        {
          href: 'https://github.com/rrake5212/zotok-platform-docs',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Documentation',
          items: [
            {
              label: 'Getting Started',
              to: '/docs/getting-started/login',
            },
            {
              label: 'Dashboard',
              to: '/docs/dashboard/overview',
            },
            {
              label: 'Campaigns',
              to: '/docs/campaigns/overview',
            },
          ],
        },
        {
          title: 'Modules',
          items: [
            {
              label: 'Sales',
              to: '/docs/sales/overview',
            },
            {
              label: 'Payments',
              to: '/docs/payments/overview',
            },
            {
              label: 'Threads',
              to: '/docs/threads/overview',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/rrake5212/zotok-platform-docs',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Hd Agencies. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
