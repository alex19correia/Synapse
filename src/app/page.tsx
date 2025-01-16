import { auth } from '@clerk/nextjs'
import { redirect } from 'next/navigation'

export default async function Home() {
  const { userId } = auth()
  
  if (!userId) {
    redirect('/login')
  }

  redirect('/chat')
} 