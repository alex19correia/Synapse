import { chromium, FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  const { baseURL } = config.projects[0].use;
  
  // Criar browser
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  
  console.log('\n🧹 Iniciando limpeza do ambiente...');
  
  // Limpar dados de teste
  try {
    await page.goto(`${baseURL}/api/test/cleanup`);
    console.log('✅ Dados de teste removidos com sucesso');
  } catch (error) {
    console.warn('⚠️ Aviso: Não foi possível limpar dados de teste');
  }
  
  // Limpar cache do Redis
  try {
    await page.goto(`${baseURL}/api/test/clear-cache`);
    console.log('✅ Cache limpo com sucesso');
  } catch (error) {
    console.warn('⚠️ Aviso: Não foi possível limpar o cache');
  }
  
  // Remover arquivos temporários
  try {
    await page.goto(`${baseURL}/api/test/clear-temp`);
    console.log('✅ Arquivos temporários removidos');
  } catch (error) {
    console.warn('⚠️ Aviso: Não foi possível remover arquivos temporários');
  }
  
  // Remover usuários de teste
  try {
    await page.goto(`${baseURL}/api/test/clear-users`);
    console.log('✅ Usuários de teste removidos');
  } catch (error) {
    console.warn('⚠️ Aviso: Não foi possível remover usuários de teste');
  }
  
  // Limpar storage state
  try {
    await context.clearCookies();
    console.log('✅ Cookies limpos com sucesso');
  } catch (error) {
    console.warn('⚠️ Aviso: Não foi possível limpar cookies');
  }
  
  // Fechar browser
  await browser.close();
  
  console.log('\n🎉 Limpeza concluída com sucesso!\n');
}

export default globalTeardown; 