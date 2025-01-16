import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  const { baseURL, storageState } = config.projects[0].use;
  
  // Criar browser
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Verificar se a aplicação está rodando
  try {
    await page.goto(baseURL!);
  } catch (error) {
    console.error('❌ Erro: A aplicação não está rodando no endereço:', baseURL);
    console.error('Por favor, inicie a aplicação com: npm run dev');
    process.exit(1);
  }
  
  // Criar usuário de teste se necessário
  try {
    await page.goto(`${baseURL}/api/test/setup`);
    const response = await page.waitForResponse('**/api/test/setup');
    const data = await response.json();
    
    if (!data.success) {
      throw new Error('Falha ao criar usuário de teste');
    }
    
    console.log('✅ Usuário de teste criado com sucesso');
  } catch (error) {
    console.warn('⚠️ Aviso: Não foi possível criar usuário de teste');
    console.warn('Alguns testes de autenticação podem falhar');
  }
  
  // Verificar serviços necessários
  const services = [
    { name: 'Banco de Dados', url: `${baseURL}/api/health/db` },
    { name: 'Redis', url: `${baseURL}/api/health/redis` }
  ];
  
  for (const service of services) {
    try {
      const response = await page.goto(service.url);
      const data = await response?.json();
      
      if (data?.status !== 'ok') {
        throw new Error(`${service.name} não está respondendo corretamente`);
      }
      
      console.log(`✅ ${service.name} está funcionando`);
    } catch (error) {
      console.error(`❌ Erro: ${service.name} não está disponível`);
      console.error('Por favor, verifique se todos os serviços estão rodando');
      process.exit(1);
    }
  }
  
  // Limpar dados de teste anteriores
  try {
    await page.goto(`${baseURL}/api/test/cleanup`);
    console.log('✅ Dados de teste anteriores limpos com sucesso');
  } catch (error) {
    console.warn('⚠️ Aviso: Não foi possível limpar dados de teste anteriores');
  }
  
  // Configurar tema claro por padrão
  await context.addInitScript(() => {
    window.localStorage.setItem('theme', 'light');
  });
  
  // Salvar estado inicial
  if (storageState) {
    await context.storageState({ path: storageState as string });
    console.log('✅ Estado inicial salvo em:', storageState);
  }
  
  // Fechar browser
  await browser.close();
  
  console.log('\n🚀 Setup global concluído com sucesso!\n');
}

export default globalSetup; 