import { auth } from '@clerk/nextjs';

export default async function TokenPage() {
  const { userId } = auth();
  
  if (!userId) {
    return (
      <div style={{ padding: '1rem' }}>
        <h1>Erro</h1>
        <p>Não foi possível obter o token. Por favor, faça login primeiro.</p>
      </div>
    );
  }

  const token = await auth().getToken();
  
  return (
    <div style={{ padding: '1rem' }}>
      <h1>Token para Testes</h1>
      <div style={{ marginTop: '1rem' }}>
        <p>Use este token nos seus testes:</p>
        <pre style={{ 
          background: '#f5f5f5', 
          padding: '1rem', 
          borderRadius: '4px',
          marginTop: '0.5rem',
          wordWrap: 'break-word'
        }}>
          {token}
        </pre>
      </div>
      
      <div style={{ marginTop: '2rem' }}>
        <h2>Como usar:</h2>
        <pre style={{ 
          background: '#f5f5f5', 
          padding: '1rem', 
          borderRadius: '4px',
          marginTop: '0.5rem'
        }}>
{`// Headers para requisição
{
  "Authorization": "Bearer ${token}",
  "Content-Type": "application/json"
}`}
        </pre>
      </div>
    </div>
  );
} 