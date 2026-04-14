import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Vastu Design Generator',
  description:
    'AI-powered architecture assistant with Vastu Shastra expertise. Generate design briefs, material specs, Vastu zoning analysis, and Midjourney prompts instantly.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
