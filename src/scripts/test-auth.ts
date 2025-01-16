import axios from 'axios';

async function testAuthFlow() {
    const BASE_URL = 'http://localhost:3001';
    const TEST_TOKEN = process.env.CLERK_TEST_TOKEN;

    console.log('🧪 Iniciando testes de autenticação...\n');

    // 1. Teste de Rate Limiting
    console.log('1️⃣ Testando Rate Limiting...');
    try {
        const requests = Array(110).fill(null);
        let rateLimited = false;
        
        await Promise.all(requests.map(async (_, i) => {
            try {
                await axios.get(`${BASE_URL}/api/debug/session`);
                process.stdout.write('.');
            } catch (error: any) {
                if (error.response?.status === 429) {
                    rateLimited = true;
                    process.stdout.write('X');
                }
            }
        }));
        
        console.log('\n✅ Rate limiting ' + (rateLimited ? 'funcionando' : 'não ativado'));
    } catch (error) {
        console.error('❌ Erro no teste de rate limiting:', error);
    }

    // 2. Teste de Autenticação
    console.log('\n2️⃣ Testando Autenticação...');
    try {
        const response = await axios.get(`${BASE_URL}/api/debug/session`, {
            headers: {
                Authorization: `Bearer ${TEST_TOKEN}`
            }
        });
        console.log('✅ Autenticação bem-sucedida:', response.data);
    } catch (error: any) {
        console.error('❌ Erro na autenticação:', error.response?.data || error.message);
    }

    // 3. Teste de MFA
    console.log('\n3️⃣ Verificando status do MFA...');
    try {
        const response = await axios.get(`${BASE_URL}/api/auth/mfa/status`, {
            headers: {
                Authorization: `Bearer ${TEST_TOKEN}`
            }
        });
        console.log('✅ Status do MFA:', response.data);
    } catch (error: any) {
        console.error('❌ Erro ao verificar MFA:', error.response?.data || error.message);
    }
}

testAuthFlow().catch(console.error); 