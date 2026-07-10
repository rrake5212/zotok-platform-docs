/**
 * Markdoc configuration with custom tags for the documentation.
 */
import Markdoc from '@markdoc/markdoc';

/**
 * Callout tag — renders Tip / Note / Warning / Success / Important
 * Usage: {% callout type="tip" %}text{% /callout %}
 */
const callout = {
  render: 'Callout',
  attributes: {
    type: { type: String, default: 'note' },
    title: { type: String, default: '' },
  },
};

/**
 * Markdoc config
 */
export const markdocConfig = {
  tags: {
    callout,
  },
  variables: {},
};

/**
 * Parse raw markdown string through Markdoc.
 * Returns { ast, frontmatter, body }
 */
export function parseMarkdoc(source) {
  const ast = Markdoc.parse(source);
  const frontmatter = ast.attributes?.frontmatter || {};
  const body = Markdoc.transform(ast, markdocConfig);
  return { ast, frontmatter, body };
}

/**
 * Extract headings from a Markdoc AST for TOC generation.
 */
export function extractHeadings(ast) {
  const headings = [];
  function walk(node) {
    if (!node) return;
    if (node.type === 'heading' && node.attributes?.level >= 2 && node.attributes?.level <= 4) {
      const text = node.children
        .filter(c => c.type === 'text' || c.type === 'inline')
        .map(c => (typeof c === 'string' ? c : c?.children?.[0] || ''))
        .join('')
        .trim();
      if (text) {
        headings.push({
          level: node.attributes.level,
          text,
          id: node.attributes.id || slugify(text),
        });
      }
    }
    if (node.children) {
      node.children.forEach(walk);
    }
  }
  walk(ast);
  return headings;
}

function slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim();
}
