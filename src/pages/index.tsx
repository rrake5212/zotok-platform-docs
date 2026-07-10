import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';

export default function Home(): JSX.Element {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title="Home"
      description="ZoTok Platform User Manual — Field Operations & Distributor Management">
      <main className="hero hero--primary" style={{padding: '4rem 0'}}>
        <div className="container">
          <h1 className="hero__title">{siteConfig.title}</h1>
          <p className="hero__subtitle">{siteConfig.tagline}</p>
          <div style={{marginTop: '2rem'}}>
            <Link
              className="button button--secondary button--lg"
              to="/docs/intro">
              📖 Read the Manual
            </Link>
          </div>
        </div>
      </main>

      <div className="container" style={{padding: '3rem 0'}}>
        <div className="row">
          <div className="col col--4">
            <div className="card" style={{height: '100%'}}>
              <div className="card__header">
                <h3>🚀 Getting Started</h3>
              </div>
              <div className="card__body">
                <p>New to ZoTok? Start here to learn the basics — login, navigation, and platform overview.</p>
              </div>
              <div className="card__footer">
                <Link className="button button--primary button--sm" to="/docs/getting-started/login">
                  Get Started
                </Link>
              </div>
            </div>
          </div>
          <div className="col col--4">
            <div className="card" style={{height: '100%'}}>
              <div className="card__header">
                <h3>📊 Dashboard</h3>
              </div>
              <div className="card__body">
                <p>Understand your KPIs, customer data, and business performance at a glance.</p>
              </div>
              <div className="card__footer">
                <Link className="button button--primary button--sm" to="/docs/dashboard/overview">
                  View Dashboard
                </Link>
              </div>
            </div>
          </div>
          <div className="col col--4">
            <div className="card" style={{height: '100%'}}>
              <div className="card__header">
                <h3>📧 Campaigns</h3>
              </div>
              <div className="card__body">
                <p>Create targeted marketing campaigns and manage customer lifecycles.</p>
              </div>
              <div className="card__footer">
                <Link className="button button--primary button--sm" to="/docs/campaigns/overview">
                  Explore Campaigns
                </Link>
              </div>
            </div>
          </div>
        </div>

        <div style={{marginTop: '3rem', textAlign: 'center'}}>
          <h2>All Modules</h2>
          <div className="row" style={{marginTop: '1.5rem'}}>
            {[
              {name: 'Sales', icon: '💰', link: '/docs/sales/overview'},
              {name: 'Payments', icon: '💳', link: '/docs/payments/overview'},
              {name: 'Products', icon: '📦', link: '/docs/products/overview'},
              {name: 'Threads', icon: '💬', link: '/docs/threads/overview'},
              {name: 'Queries', icon: '❓', link: '/docs/queries/overview'},
              {name: 'Customers', icon: '👥', link: '/docs/customers/overview'},
              {name: 'Orders', icon: '📋', link: '/docs/orders/overview'},
              {name: 'Invoices', icon: '🧾', link: '/docs/invoices/overview'},
              {name: 'Ledger', icon: '📒', link: '/docs/ledger/overview'},
              {name: 'Schemes', icon: '🏷️', link: '/docs/schemes/overview'},
              {name: 'Field Ops', icon: '📍', link: '/docs/field-ops/overview'},
              {name: 'Day Book', icon: '📖', link: '/docs/day-book/overview'},
            ].map(mod => (
              <div className="col col--3" key={mod.name} style={{marginBottom: '1rem'}}>
                <Link
                  to={mod.link}
                  style={{
                    display: 'block',
                    padding: '1rem',
                    border: '1px solid var(--ifm-color-emphasis-200)',
                    borderRadius: '8px',
                    textDecoration: 'none',
                    color: 'var(--ifm-font-color-base)',
                    fontWeight: 500,
                  }}>
                  {mod.icon} {mod.name}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}
