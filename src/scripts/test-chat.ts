import { config } from 'dotenv';
import { resolve } from 'path';

// Carrega as variáveis de ambiente do arquivo .env na raiz do projeto
config({ path: resolve(__dirname, '../../.env') });

import { db } from '@/lib/db';

async function testChat() {
  try {
    console.log('🚀 Iniciando testes do chat...\n');

    // 1. Criar uma nova sessão
    console.log('1. Criando nova sessão de chat...');
    const session = await db.createChatSession('test-user', 'Sessão de Teste');
    console.log('✅ Sessão criada:', session);
    console.log();

    // 2. Adicionar algumas mensagens
    console.log('2. Adicionando mensagens...');
    const message1 = await db.addMessage(session.id, 'user', 'Olá, como está?');
    console.log('✅ Mensagem do usuário adicionada:', message1);
    
    const message2 = await db.addMessage(session.id, 'assistant', 'Olá! Estou bem, como posso ajudar?');
    console.log('✅ Mensagem do assistente adicionada:', message2);
    console.log();

    // 3. Buscar mensagens da sessão
    console.log('3. Buscando mensagens da sessão...');
    const messages = await db.getMessages(session.id);
    console.log('✅ Mensagens encontradas:', messages.length);
    console.log();

    // 4. Buscar todas as sessões do usuário
    console.log('4. Buscando sessões do usuário...');
    const sessions = await db.getChatSessions('test-user');
    console.log('✅ Sessões encontradas:', sessions.length);
    console.log();

    // 5. Atualizar status da sessão
    console.log('5. Atualizando status da sessão...');
    await db.archiveChatSession(session.id);
    const updatedSession = await db.getChatSession(session.id);
    console.log('✅ Sessão atualizada:', updatedSession);
    console.log();

    // 6. Deletar a sessão de teste
    console.log('6. Deletando sessão de teste...');
    await db.deleteChatSession(session.id);
    console.log('✅ Sessão deletada com sucesso');
    
    console.log('\n🎉 Todos os testes completados com sucesso!');
  } catch (error) {
    console.error('\n❌ Erro durante os testes:', error);
  }
}

testChat(); 