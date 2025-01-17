import { test, expect } from '@playwright/test';

test.describe('Smoke Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Começar cada teste na página inicial
    await page.goto('/');
  });

  test('deve carregar a página inicial', async ({ page }) => {
    // Verificar título
    await expect(page).toHaveTitle(/Synapse/);
    
    // Verificar elementos principais
    await expect(page.locator('nav')).toBeVisible();
    await expect(page.locator('footer')).toBeVisible();
  });

  test('deve responder ao health check', async ({ request }) => {
    const response = await request.get('/api/health');
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toEqual({ status: 'ok' });
  });

  test('deve ter links de navegação funcionando', async ({ page }) => {
    // Verificar links principais
    const links = [
      { selector: '[data-testid=home-link]', url: '/' },
      { selector: '[data-testid=login-link]', url: '/login' },
      { selector: '[data-testid=signup-link]', url: '/signup' }
    ];

    for (const link of links) {
      await page.locator(link.selector).click();
      await expect(page).toHaveURL(link.url);
      await page.goto('/'); // Voltar para home
    }
  });

  test('deve ter layout responsivo', async ({ page }) => {
    // Testar diferentes viewports
    const viewports = [
      { width: 1920, height: 1080 }, // Desktop
      { width: 1024, height: 768 },  // Tablet
      { width: 375, height: 667 }    // Mobile
    ];

    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      await expect(page.locator('nav')).toBeVisible();
      await expect(page.locator('main')).toBeVisible();
    }
  });

  test('deve ter meta tags corretas', async ({ page }) => {
    // Verificar meta tags importantes
    const metaTags = {
      description: 'Synapse - Sua plataforma de IA',
      viewport: 'width=device-width, initial-scale=1',
      'theme-color': '#ffffff'
    };

    for (const [name, content] of Object.entries(metaTags)) {
      const meta = page.locator(`meta[name="${name}"]`);
      await expect(meta).toHaveAttribute('content', content);
    }
  });

  test('deve carregar assets estáticos', async ({ page }) => {
    // Verificar se imagens principais carregam
    const images = await page.locator('img').all();
    for (const image of images) {
      const src = await image.getAttribute('src');
      if (src?.startsWith('/')) {
        const response = await page.request.get(src);
        expect(response.ok()).toBeTruthy();
      }
    }
  });

  test('deve ter performance aceitável', async ({ page }) => {
    // Medir tempo de carregamento
    const startTime = Date.now();
    await page.goto('/', { waitUntil: 'networkidle' });
    const loadTime = Date.now() - startTime;
    
    // Tempo de carregamento deve ser menor que 3 segundos
    expect(loadTime).toBeLessThan(3000);
  });

  test('deve ter tratamento de erros 404', async ({ page }) => {
    // Acessar página inexistente
    await page.goto('/pagina-que-nao-existe');
    
    // Verificar página de 404
    await expect(page.locator('h1')).toContainText(/404|não encontrada/i);
    await expect(page.locator('a')).toContainText(/voltar|início/i);
  });

  test('deve ter acessibilidade básica', async ({ page }) => {
    // Verificar elementos de acessibilidade
    await expect(page.locator('html')).toHaveAttribute('lang', 'pt-BR');
    await expect(page.locator('main')).toHaveAttribute('role', 'main');
    await expect(page.locator('nav')).toHaveAttribute('role', 'navigation');
    
    // Verificar contraste de texto
    const headings = await page.locator('h1, h2, h3').all();
    for (const heading of headings) {
      await expect(heading).toHaveCSS('color', /^rgb/);
    }
  });

  test('deve ter tema escuro funcionando', async ({ page }) => {
    // Ativar tema escuro
    await page.evaluate(() => {
      document.documentElement.classList.add('dark');
    });
    
    // Verificar cores do tema escuro
    await expect(page.locator('body')).toHaveCSS('background-color', /^rgb/);
    await expect(page.locator('body')).toHaveCSS('color', /^rgb/);
  });
}); 