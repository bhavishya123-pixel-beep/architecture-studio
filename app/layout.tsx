import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'FORMA — Furniture for the way you live',
  description:
    'Minimal luxury furniture crafted from the world\'s finest materials. Solid oak, Italian leather, Carrara marble. Designed to endure.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
