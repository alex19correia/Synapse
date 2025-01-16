import { resolve } from 'path';
import dotenv from 'dotenv';
import { db } from '../lib/db';
import { createClerkClient } from '@clerk/clerk-sdk-node';

// Carregar variáveis de ambiente
dotenv.config({ path: resolve(__dirname, '../../.env') });

async function main() {
  try {
    // Testar Clerk
    const clerk = createClerkClient({ secretKey: process.env.CLERK_SECRET_KEY });
    const userList = await clerk.users.getUserList();
    console.log('Usuários:', userList.data.length);

    // Testar banco de dados
    if (userList.data.length > 0) {
      const userId = userList.data[0].id;
      const sessions = await db.getChatSessions(userId);
      console.log('Sessões do usuário:', sessions.length);
    }

  } catch (error) {
    console.error('Erro:', error);
  }
}

main(); 