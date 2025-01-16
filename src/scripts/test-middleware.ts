import axios from 'axios';

async function testMiddleware() {
    const API_URL = 'http://localhost:3000/api';
    // Token válido do Clerk (deve ser obtido do ambiente)
    const CLERK_TOKEN = process.env.CLERK_TEST_TOKEN;
    
    console.log('🧪 Iniciando testes do middleware...\n');

    // Teste 1: Rota não autenticada
    try {
        console.log('Teste 1: Tentando acessar rota protegida sem autenticação...');
        await axios.get(`${API_URL}/protected`);
    } catch (error: any) {
        console.log('✅ Erro esperado:', error.response.status);
    }

    // Teste 2: Rate Limiting
    console.log('\nTeste 2: Testando rate limiting...');
    const requests = Array(110).fill(null);
    let rateLimited = false;

    try {
        await Promise.all(
            requests.map(async () => {
                try {
                    await axios.get(`${API_URL}/public`);
                } catch (error: any) {
                    if (error.response.status === 429) {
                        rateLimited = true;
                    }
                }
            })
        );

        console.log('✅ Rate limiting funcionando:', rateLimited);
    } catch (error) {
        console.log('❌ Erro no teste de rate limiting:', error);
    }

    // Teste 3: Autenticação com token válido
    try {
        console.log('\nTeste 3: Testando autenticação com token válido...');
        if (!CLERK_TOKEN) {
            console.log('⚠️ CLERK_TEST_TOKEN não encontrado no ambiente. Pulando teste de autenticação.');
            return;
        }

        const response = await axios.get(`${API_URL}/protected`, {
            headers: {
                Authorization: `Bearer ${CLERK_TOKEN}`
            }
        });
        console.log('✅ Autenticação funcionando:', response.status === 200);
    } catch (error) {
        console.log('❌ Erro no teste de autenticação:', error);
    }
}

testMiddleware().catch(console.error); 