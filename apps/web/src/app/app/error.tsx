'use client'

import Link from 'next/link'
import { useEffect } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-4">500</h1>
      <h2 className="text-2xl font-bold mb-4">Erro do servidor</h2>
      <p className="mb-4">Ocorreu um erro no servidor. Por favor, tente novamente mais tarde.</p>
      <div className="flex gap-4">
        <button
          onClick={() => reset()}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Tentar novamente
        </button>
        <Link 
          href="/"
          className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
        >
          Voltar ao início
        </Link>
      </div>
    </div>
  )
} 