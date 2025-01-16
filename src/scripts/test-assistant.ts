import { AssistantsClient } from '../lib/assistants/client';
import { getAssistantConfig } from '../lib/assistants/config';
import dotenv from 'dotenv';

// Carregar variáveis de ambiente
dotenv.config();

async function testAssistant() {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    console.error('❌ OPENAI_API_KEY não encontrada nas variáveis de ambiente');
    process.exit(1);
  }

  console.log('🤖 Iniciando teste do Assistente...');

  const client = new AssistantsClient(apiKey, getAssistantConfig());

  try {
    console.log('📝 Inicializando assistente...');
    await client.initialize();
    console.log('✅ Assistente inicializado com sucesso!');

    console.log('🧵 Criando thread...');
    const thread = await client.createThread();
    console.log('✅ Thread criado:', thread);

    const testQuestion = 'Qual é a melhor maneira de implementar autenticação em uma API Node.js?';
    console.log(`💬 Enviando pergunta: "${testQuestion}"`);
    
    const response = await client.sendMessage(thread.threadId, testQuestion);
    console.log('✅ Mensagem enviada, aguardando resposta...');

    let threadState = await client.getThreadState(thread.threadId);
    while (threadState.status === 'active') {
      process.stdout.write('.');
      await new Promise(resolve => setTimeout(resolve, 1000));
      threadState = await client.getThreadState(thread.threadId);
    }

    console.log('\n\n📨 Resposta recebida:');
    console.log(threadState.lastMessage?.content);

  } catch (error) {
    console.error('❌ Erro durante o teste:', error);
  }
}

// Executar o teste
testAssistant(); 