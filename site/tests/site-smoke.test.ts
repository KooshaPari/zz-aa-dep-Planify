import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

// ---------------------------------------------------------------------------
// Paths (relative to this test file)
// ---------------------------------------------------------------------------
const SITE_ROOT = resolve(import.meta.dirname ?? __dirname, '..');

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function loadJson(relPath: string): Record<string, unknown> {
  const raw = readFileSync(resolve(SITE_ROOT, relPath), 'utf-8');
  return JSON.parse(raw) as Record<string, unknown>;
}

// ===========================================================================
// 1. Astro configuration
// ===========================================================================
describe('Astro config', () => {
  it('astro.config.mjs is valid ESM and exports a default config', async () => {
    const mod = await import(resolve(SITE_ROOT, 'astro.config.mjs'));
    expect(mod.default).toBeDefined();
  });

  it('configures the site URL', async () => {
    const mod = await import(resolve(SITE_ROOT, 'astro.config.mjs'));
    expect(mod.default.site).toBe('https://planify.space');
  });

  it('configures the Vite plugin array', async () => {
    const mod = await import(resolve(SITE_ROOT, 'astro.config.mjs'));
    expect(Array.isArray(mod.default.vite?.plugins)).toBe(true);
  });
});

// ===========================================================================
// 2. data/config.json – site metadata
// ===========================================================================
describe('data/config.json', () => {
  const config = loadJson('data/config.json');

  it('has required fields', () => {
    for (const key of ['name', 'slug', 'domain', 'description', 'tier', 'repo']) {
      expect(config).toHaveProperty(key);
    }
  });

  it('domain matches the Astro site URL', () => {
    expect(config.domain).toBe('planify.space');
  });

  it('features is a non-empty array', () => {
    expect(Array.isArray(config.features)).toBe(true);
    expect((config.features as unknown[]).length).toBeGreaterThan(0);
  });

  it('links object contains github and upstream', () => {
    const links = config.links as Record<string, string>;
    expect(links.github).toBeDefined();
    expect(links.upstream).toBeDefined();
  });
});

// ===========================================================================
// 3. package.json – project metadata
// ===========================================================================
describe('package.json', () => {
  const pkg = loadJson('package.json');

  it('is named planify-space', () => {
    expect(pkg.name).toBe('planify-space');
  });

  it('declares type module', () => {
    expect(pkg.type).toBe('module');
  });

  it('has expected scripts', () => {
    const scripts = pkg.scripts as Record<string, string>;
    expect(scripts).toHaveProperty('dev');
    expect(scripts).toHaveProperty('build');
    expect(scripts).toHaveProperty('test');
  });

  it('has core dependencies', () => {
    const deps = pkg.dependencies as Record<string, string>;
    expect(deps).toHaveProperty('astro');
    expect(deps).toHaveProperty('tailwindcss');
    expect(deps).toHaveProperty('three');
  });

  it('has vitest as a devDependency', () => {
    const allDeps = { ...pkg.dependencies, ...pkg.devDependencies } as Record<string, string>;
    expect(allDeps).toHaveProperty('vitest');
  });
});

// ===========================================================================
// 4. tsconfig.json – TypeScript configuration
// ===========================================================================
describe('tsconfig.json', () => {
  const tsconfig = loadJson('tsconfig.json');

  it('extends astro/tsconfigs/strict', () => {
    expect(tsconfig.extends).toBe('astro/tsconfigs/strict');
  });

  it('defines the ~/* path alias to src/*', () => {
    const paths = (tsconfig.compilerOptions as Record<string, unknown>).paths as Record<string, string[]>;
    expect(paths).toHaveProperty('~/*');
    expect(paths['~/*']).toContain('src/*');
  });
});

// ===========================================================================
// 5. vercel.json – deployment config
// ===========================================================================
describe('vercel.json', () => {
  const vercel = loadJson('vercel.json');

  it('sets framework to astro', () => {
    expect(vercel.framework).toBe('astro');
  });

  it('uses bun for build/install commands', () => {
    expect(vercel.buildCommand).toContain('bun');
    expect(vercel.installCommand).toContain('bun');
  });

  it('outputDirectory is dist', () => {
    expect(vercel.outputDirectory).toBe('dist');
  });
});
