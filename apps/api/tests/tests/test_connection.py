import asyncio
from src.database import db
from loguru import logger

async def test_supabase_connection():
    """Testa a conexão com o Supabase e operações básicas."""
    try:
        # Teste 1: Criar um utilizador de teste
        test_user = {
            'email': 'teste@exemplo.com',
            'name': 'Utilizador Teste'
        }
        
        logger.info("🔍 A testar criação de utilizador...")
        user = await db.create_user(test_user)
        if user:
            logger.success("✅ Utilizador criado com sucesso!")
            logger.info(f"Dados do utilizador: {user}")
        
        # Teste 2: Procurar o utilizador por email
        logger.info("🔍 A procurar utilizador por email...")
        found_user = await db.get_user_by_email('teste@exemplo.com')
        if found_user:
            logger.success("✅ Utilizador encontrado!")
            logger.info(f"Dados do utilizador: {found_user}")
        
        # Teste 3: Criar uma sessão de chat
        if found_user:
            logger.info("🔍 A criar sessão de chat...")
            session = await db.create_chat_session(found_user['id'], "Sessão de Teste")
            if session:
                logger.success("✅ Sessão de chat criada com sucesso!")
                logger.info(f"Dados da sessão: {session}")
        
                # Teste 4: Adicionar uma mensagem
                logger.info("🔍 A adicionar mensagem...")
                message = await db.add_message(
                    session['id'],
                    'user',
                    'Olá, isto é uma mensagem de teste!'
                )
                if message:
                    logger.success("✅ Mensagem adicionada com sucesso!")
                    logger.info(f"Dados da mensagem: {message}")
        
                # Teste 5: Obter histórico de chat
                logger.info("🔍 A obter histórico de chat...")
                history = await db.get_chat_history(session['id'])
                if history:
                    logger.success("✅ Histórico obtido com sucesso!")
                    logger.info(f"Número de mensagens: {len(history)}")

    except Exception as e:
        logger.error(f"❌ Erro durante os testes: {e}")

if __name__ == "__main__":
    logger.info("🚀 A iniciar testes de conexão com Supabase...")
    asyncio.run(test_supabase_connection()) 