import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-4">404</h1>
      <h2 className="text-2xl font-bold mb-4">Página não encontrada</h2>
      <p className="mb-4">A página que procura não existe ou foi movida.</p>
      <Link 
        href="/"
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
      >
        Voltar ao início
      </Link>
    </div>
  )
} 