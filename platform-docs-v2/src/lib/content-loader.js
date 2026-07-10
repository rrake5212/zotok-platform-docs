/**
 * Content loader — uses Vite's import.meta.glob to load all markdown files
 * at build time, then parses them through Markdoc.
 *
 * Markdown files are stored in src/content/ with the same folder structure
 * as the original Docusaurus docs/ directory, e.g.:
 *   src/content/intro.md
 *   src/content/getting-started/login.md
 *   src/content/dashboard/overview.md
 */
import Markdoc from '@markdoc/markdoc';
import React from 'react';
import Callout from '../components/Callout.jsx';
import { markdocConfig, extractHeadings } from './markdoc.js';

// Import all markdown files as raw strings at build time
const modules = import.meta.glob('/src/content/**/*.md', {
  query: '?raw',
  import: 'default',
  eager: true,
});

// Pre-parsed content cache
const contentCache = new Map();
const headingCache = new Map();

/**
 * Get parsed content for a doc path.
 * Path format: "intro" or "dashboard/overview" (no leading slash, no .md)
 */
export function getDocContent(docPath) {
  if (contentCache.has(docPath)) {
    return contentCache.get(docPath);
  }

  // Try multiple path resolutions
  const candidates = [
    `/src/content/${docPath}.md`,
    `/src/content/${docPath}/index.md`,
    `/src/content/${docPath}/overview.md`,
  ];

  let raw = null;
  let matchedPath = null;
  for (const candidate of candidates) {
    if (modules[candidate]) {
      raw = modules[candidate];
      matchedPath = candidate;
      break;
    }
  }

  // Also search for partial matches (e.g., user types "campaigns/overview" but file is at campaigns/overview.md)
  if (!raw) {
    for (const [key, value] of Object.entries(modules)) {
      if (key.endsWith(`/${docPath}.md`) || key === `/src/content/${docPath}.md`) {
        raw = value;
        matchedPath = key;
        break;
      }
    }
  }

  if (!raw) {
    contentCache.set(docPath, null);
    return null;
  }

  // Parse frontmatter manually (simple YAML)
  const frontmatter = {};
  const bodyMatch = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  let bodyContent = raw;

  if (bodyMatch) {
    const fmLines = bodyMatch[1].split('\n');
    for (const line of fmLines) {
      const colonIdx = line.indexOf(':');
      if (colonIdx > 0) {
        const key = line.slice(0, colonIdx).trim();
        const val = line.slice(colonIdx + 1).trim().replace(/^["']|["']$/g, '');
        frontmatter[key] = val;
      }
    }
    bodyContent = bodyMatch[2];
  }

  // Parse through Markdoc
  const ast = Markdoc.parse(bodyContent);
  const transformed = Markdoc.transform(ast, markdocConfig);
  const headings = extractHeadings(ast);

  // Render to React
  let rendered = null;
  try {
    rendered = Markdoc.renderers.react(transformed, React, {
      components: {
        Callout,
      },
    });
  } catch (e) {
    console.error(`Markdoc render error for ${docPath}:`, e);
    rendered = React.createElement('pre', null, `Error rendering: ${e.message}`);
  }

  const result = {
    frontmatter,
    headings,
    rendered,
    raw: bodyContent,
    sourcePath: matchedPath,
  };

  contentCache.set(docPath, result);
  headingCache.set(docPath, headings);
  return result;
}

/**
 * Get all available document IDs.
 */
export function getAllDocIds() {
  const ids = [];
  for (const key of Object.keys(modules)) {
    // Convert /src/content/dashboard/overview.md -> dashboard/overview
    const id = key
      .replace('/src/content/', '')
      .replace(/\.md$/, '')
      .replace(/\/index$/, '');
    ids.push(id);
  }
  return ids.sort();
}

/**
 * Get TOC headings for a doc.
 */
export function getDocHeadings(docPath) {
  if (headingCache.has(docPath)) {
    return headingCache.get(docPath);
  }
  const doc = getDocContent(docPath);
  return doc ? doc.headings : [];
}

/**
 * Get label from a doc path (e.g., "dashboard/overview" → "Overview")
 */
export function getDocLabel(docPath) {
  const parts = docPath.split('/');
  const name = parts[parts.length - 1];
  return name
    .replace(/-/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase());
}
