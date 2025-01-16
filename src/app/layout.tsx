/** @generated-by-lovable - DO NOT EDIT */
import { Metadata } from 'next'
import { Providers } from './providers'
import './globals.css'

export const metadata: Metadata = {
  title: 'Synapse Assistant',
  description: 'Your personal AI assistant',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt">
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
/** @end-lovable */ 