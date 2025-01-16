import { NextApiRequest, NextApiResponse } from 'next'

const METRICS_API = process.env.METRICS_API || 'http://localhost:8000'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const { type } = req.query
  const data = req.body

  try {
    const response = await fetch(`${METRICS_API}/metrics/${type}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      throw new Error(`Metrics API returned ${response.status}`)
    }

    res.status(200).json({ success: true })
  } catch (error) {
    console.error('Error tracking metric:', error)
    res.status(500).json({ error: 'Failed to track metric' })
  }
} 