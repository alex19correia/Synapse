import { LLMProviderFactory, Message } from '@/lib/llm/providers';
import dotenv from 'dotenv';

// Carregar variáveis de ambiente
dotenv.config();

async function testProviders() {
  const factory = LLMProviderFactory.getInstance();
  
  // Teste com OpenAI
  console.log('🤖 Testando OpenAI Provider...');
  try {
    const openaiProvider = factory.createProvider('openai', {
      apiKey: process.env.OPENAI_API_KEY!,
      model: 'gpt-4-turbo-preview'
    });

    const messages: Message[] = [
      { role: 'user', content: 'Explique o conceito de programação funcional em uma frase.' }
    ];

    console.log('📤 Enviando requisição...');
    const response = await openaiProvider.generateResponse(messages);
    console.log('📥 Resposta:', response.content);
    console.log('📊 Uso de tokens:', response.usage);
  } catch (error) {
    console.error('❌ Erro no teste OpenAI:', error);
  }

  // Teste com Anthropic
  console.log('\n🤖 Testando Anthropic Provider...');
  try {
    const anthropicProvider = factory.createProvider('anthropic', {
      apiKey: process.env.ANTHROPIC_API_KEY!,
      model: 'claude-3-opus-20240229'
    });

    const messages: Message[] = [
      { role: 'user', content: 'Explique o conceito de programação funcional em uma frase.' }
    ];

    console.log('📤 Enviando requisição...');
    const response = await anthropicProvider.generateResponse(messages);
    console.log('📥 Resposta:', response.content);
  } catch (error) {
    console.error('❌ Erro no teste Anthropic:', error);
  }

  // Teste de Stream com OpenAI
  console.log('\n🤖 Testando OpenAI Stream...');
  try {
    const openaiProvider = factory.createProvider('openai', {
      apiKey: process.env.OPENAI_API_KEY!,
      model: 'gpt-4-turbo-preview'
    });

    const messages: Message[] = [
      { role: 'user', content: 'Conte uma história curta sobre um programador e sua IA assistente.' }
    ];

    console.log('📤 Iniciando stream...');
    process.stdout.write('📥 Resposta: ');
    for await (const chunk of openaiProvider.streamResponse(messages)) {
      process.stdout.write(chunk);
    }
    console.log('\n✅ Stream concluído');
  } catch (error) {
    console.error('❌ Erro no teste de stream OpenAI:', error);
  }

  // Teste de Stream com Anthropic
  console.log('\n🤖 Testando Anthropic Stream...');
  try {
    const anthropicProvider = factory.createProvider('anthropic', {
      apiKey: process.env.ANTHROPIC_API_KEY!,
      model: 'claude-3-opus-20240229'
    });

    const messages: Message[] = [
      { role: 'user', content: 'Conte uma história curta sobre um programador e sua IA assistente, mas em português de Portugal.' }
    ];

    console.log('📤 Iniciando stream...');
    process.stdout.write('📥 Resposta: ');
    for await (const chunk of anthropicProvider.streamResponse(messages)) {
      process.stdout.write(chunk);
    }
    console.log('\n✅ Stream concluído');
  } catch (error) {
    console.error('❌ Erro no teste de stream Anthropic:', error);
  }
}

// Executar testes
console.log('🚀 Iniciando testes dos providers...\n');
testProviders(); 