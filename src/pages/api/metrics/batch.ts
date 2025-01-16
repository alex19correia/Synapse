import { NextApiRequest, NextApiResponse } from 'next'

const METRICS_API = process.env.METRICS_API || 'http://localhost:8000'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const metrics = req.body
  if (!Array.isArray(metrics)) {
    return res.status(400).json({ error: 'Invalid batch format' })
  }

  try {
    const response = await fetch(`${METRICS_API}/metrics/batch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Batch-Size': req.headers['x-batch-size'] as string
      },
      body: JSON.stringify(metrics)
    })

    if (!response.ok) {
      throw new Error(`Metrics API returned ${response.status}`)
    }

    res.status(200).json({ success: true })
  } catch (error) {
    console.error('Error processing metric batch:', error)
    res.status(500).json({ error: 'Failed to process metric batch' })
  }
} 