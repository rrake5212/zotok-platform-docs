/**
 * Search module — builds a search index from all markdown content
 * at build time and provides fuzzy search via Fuse.js.
 */
import Fuse from 'fuse.js';

// Import all markdown files as raw strings (same pattern as content-loader)
const modules = import.meta.glob('/src/content/**/*.md', {
  query: '?raw',
  import: 'default',
  eager: true,
});

let fuseInstance = null;
let searchIndex = [];

/**
 * Build the search index from all markdown files.
 * Extracts title, description, headings, and body text.
 */
function buildIndex() {
  if (searchIndex.length > 0) return; // Already built

  for (const [path, raw] of Object.entries(modules)) {
    // Extract frontmatter
    const fmMatch = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
    let title = '';
    let body = raw;

    if (fmMatch) {
      const fmLines = fmMatch[1].split('\n');
      for (const line of fmLines) {
        const colonIdx = line.indexOf(':');
        if (colonIdx > 0) {
          const key = line.slice(0, colonIdx).trim();
          const val = line.slice(colonIdx + 1).trim().replace(/^["']|["']$/g, '');
          if (key === 'title') title = val;
        }
      }
      body = fmMatch[2];
    }

    // Extract headings
    const headings = [];
    const headingRegex = /^(#{2,4})\s+(.+)$/gm;
    let match;
    while ((match = headingRegex.exec(body)) !== null) {
      headings.push(match[2].trim());
    }

    // Clean body text (remove markdown syntax)
    const cleanBody = body
      .replace(/^---[\s\S]*?---\n/, '')  // Remove frontmatter
      .replace(/[#*`_\[\]()>|:-]/g, ' ')   // Remove markdown chars
      .replace(/\s+/g, ' ')                // Collapse whitespace
      .trim();

    // Derive doc path from module path
    const docPath = path
      .replace('/src/content/', '')
      .replace(/\.md$/, '')
      .replace(/\/index$/, '');

    // Derive label from path
    const parts = docPath.split('/');
    const label = parts[parts.length - 1]
      .replace(/-/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());

    searchIndex.push({
      id: docPath,
      title: title || label,
      path: `/docs/${docPath}`,
      headings: headings.slice(0, 10),
      body: cleanBody.slice(0, 2000),
    });
  }

  // Initialize Fuse
  fuseInstance = new Fuse(searchIndex, {
    keys: [
      { name: 'title', weight: 3 },
      { name: 'headings', weight: 2 },
      { name: 'body', weight: 1 },
    ],
    threshold: 0.4,
    includeScore: true,
    minMatchCharLength: 2,
  });
}

/**
 * Search for documents matching the query.
 * Returns results sorted by relevance.
 */
export function search(query) {
  buildIndex();
  if (!query || query.trim().length < 2) return [];
  const results = fuseInstance.search(query.trim());
  return results.slice(0, 10).map(r => ({
    ...r.item,
    score: r.score,
  }));
}

/**
 * Get all indexed documents (for building a sitemap or listing).
 */
export function getAllSearchEntries() {
  buildIndex();
  return searchIndex;
}

// Build index immediately on module load
buildIndex();
