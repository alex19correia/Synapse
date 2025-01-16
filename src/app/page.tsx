export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-4">Synapse Assistant</h1>
      <p className="text-xl mb-8">Seu assistente pessoal de IA</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 border rounded-lg shadow-sm hover:shadow-md transition-shadow">
          <h2 className="text-2xl font-semibold mb-2">Chat Inteligente</h2>
          <p>Converse naturalmente e obtenha respostas precisas</p>
        </div>
        <div className="p-6 border rounded-lg shadow-sm hover:shadow-md transition-shadow">
          <h2 className="text-2xl font-semibold mb-2">Personalizado</h2>
          <p>Adaptado às suas necessidades específicas</p>
        </div>
      </div>
    </main>
  )
} 