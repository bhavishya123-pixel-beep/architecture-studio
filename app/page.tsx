'use client'

import { useState, useCallback, useRef } from 'react'

// ─── Types ────────────────────────────────────────────────────────────────────

type SectionKey = 'brief' | 'materials' | 'vastu' | 'midjourney'

interface Section {
  key: SectionKey
  marker: string
  title: string
  emoji: string
  borderClass: string
  dotClass: string
}

// ─── Config ───────────────────────────────────────────────────────────────────

const EXAMPLES = [
  'open plan living room, Vastu compliant, earthy tones, high ceiling, exposed stone',
  'master bedroom, southwest corner, warm terracotta palette, built-in wooden wardrobe',
  'home office, northeast corner, natural light, zen aesthetic, bamboo and linen',
  'kitchen, southeast zone, bright and airy, white marble, modern farmhouse style',
]

const SECTIONS: Section[] = [
  {
    key: 'brief',
    marker: '## DESIGN BRIEF',
    title: 'Design Brief',
    emoji: '📐',
    borderClass: 'border-amber-800/70',
    dotClass: 'bg-amber-600',
  },
  {
    key: 'materials',
    marker: '## MATERIALS & DIMENSIONS',
    title: 'Materials & Dimensions',
    emoji: '🧱',
    borderClass: 'border-orange-800/70',
    dotClass: 'bg-orange-700',
  },
  {
    key: 'vastu',
    marker: '## VASTU ZONING',
    title: 'Vastu Zoning',
    emoji: '🧿',
    borderClass: 'border-stone-500/60',
    dotClass: 'bg-stone-500',
  },
  {
    key: 'midjourney',
    marker: '## MIDJOURNEY PROMPTS',
    title: 'Midjourney Prompts',
    emoji: '✨',
    borderClass: 'border-violet-800/70',
    dotClass: 'bg-violet-700',
  },
]

// ─── Helpers ──────────────────────────────────────────────────────────────────

function extractSection(fullText: string, marker: string): string {
  const allMarkers = SECTIONS.map((s) => s.marker)
  const startIdx = fullText.indexOf(marker)
  if (startIdx === -1) return ''
  const contentStart = startIdx + marker.length
  let endIdx = fullText.length
  for (const m of allMarkers) {
    if (m === marker) continue
    const idx = fullText.indexOf(m, contentStart)
    if (idx !== -1 && idx < endIdx) endIdx = idx
  }
  return fullText.slice(contentStart, endIdx).trim()
}

function parseBoldInline(text: string): React.ReactNode {
  const parts = text.split(/(\*\*[^*]+\*\*)/)
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i} className="text-stone-200 font-semibold">{part.slice(2, -2)}</strong>
    }
    return part
  })
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function TextLine({ line }: { line: string }) {
  const t = line.trim()

  if (!t || t === '---' || t === '***') {
    return <div className="h-2" />
  }

  // Horizontal rule (dashes)
  if (/^-{3,}$/.test(t) || /^={3,}$/.test(t)) {
    return <hr className="border-stone-800 my-3" />
  }

  // Subheading (### or **)
  if (t.startsWith('### ')) {
    return (
      <p className="text-stone-200 font-semibold text-sm mt-4 mb-1">
        {t.slice(4)}
      </p>
    )
  }
  if (/^\*\*[^*]+\*\*:?$/.test(t)) {
    return (
      <p className="text-stone-200 font-semibold text-sm mt-3 mb-0.5">
        {t.replace(/\*\*/g, '').replace(/:$/, '')}
      </p>
    )
  }

  // Bullet point
  if (t.startsWith('- ') || t.startsWith('• ') || t.startsWith('* ')) {
    const content = t.slice(2)
    return (
      <div className="flex gap-2 items-start py-0.5">
        <span className="text-amber-600 text-xs mt-[5px] shrink-0 select-none">▸</span>
        <span className="text-stone-300 text-sm leading-relaxed">
          {parseBoldInline(content)}
        </span>
      </div>
    )
  }

  // Numbered list
  const numMatch = t.match(/^(\d+)\.\s+(.+)/)
  if (numMatch) {
    return (
      <div className="flex gap-2 items-start py-0.5">
        <span className="text-amber-700 text-xs mt-[5px] shrink-0 tabular-nums w-4">
          {numMatch[1]}.
        </span>
        <span className="text-stone-300 text-sm leading-relaxed">
          {parseBoldInline(numMatch[2])}
        </span>
      </div>
    )
  }

  // Table row (| ... |)
  if (t.startsWith('|')) {
    const cells = t.split('|').filter((c) => c.trim())
    if (cells.every((c) => /^[-: ]+$/.test(c))) return null // separator row
    return (
      <div className="flex gap-3 text-xs py-0.5 border-b border-stone-800/50">
        {cells.map((cell, i) => (
          <span key={i} className={`text-stone-300 ${i === 0 ? 'font-medium text-stone-200 w-28 shrink-0' : ''}`}>
            {cell.trim()}
          </span>
        ))}
      </div>
    )
  }

  return (
    <p className="text-stone-300 text-sm leading-relaxed">
      {parseBoldInline(t)}
    </p>
  )
}

function SectionContent({ text, isStreaming }: { text: string; isStreaming: boolean }) {
  const lines = text.split('\n')
  return (
    <div className="space-y-0.5">
      {lines.map((line, i) => (
        <TextLine key={i} line={line} />
      ))}
      {isStreaming && <span className="cursor-blink" />}
    </div>
  )
}

function MidjourneyContent({
  text,
  onCopy,
  copied,
  isStreaming,
}: {
  text: string
  onCopy: (t: string, k: string) => void
  copied: string | null
  isStreaming: boolean
}) {
  const lines = text.split('\n')
  const prompts = lines.filter((l) => l.trim().startsWith('/imagine'))
  const introLines = lines.filter(
    (l) => !l.trim().startsWith('/imagine') && l.trim()
  )

  return (
    <div>
      {introLines.length > 0 && (
        <div className="mb-4 space-y-0.5">
          {introLines.map((line, i) => (
            <TextLine key={i} line={line} />
          ))}
        </div>
      )}
      <div className="space-y-3">
        {prompts.map((prompt, i) => (
          <div key={i} className="group relative">
            <div className="bg-stone-950 border border-stone-800 rounded-lg p-3 text-xs font-mono text-stone-400 leading-relaxed break-all pr-14">
              {prompt.trim()}
            </div>
            <button
              onClick={() => onCopy(prompt.trim(), `p${i}`)}
              className="absolute right-2 top-2 px-2 py-1 text-xs bg-stone-800 hover:bg-stone-700 text-stone-500 hover:text-stone-200 rounded transition-all opacity-0 group-hover:opacity-100"
            >
              {copied === `p${i}` ? '✓' : 'Copy'}
            </button>
          </div>
        ))}
        {prompts.length === 0 && isStreaming && (
          <span className="cursor-blink text-stone-700 text-sm" />
        )}
      </div>
    </div>
  )
}

function EmptyCard({ isLoading }: { isLoading: boolean }) {
  return (
    <div className="flex items-center justify-center h-40">
      {isLoading ? (
        <div className="flex items-center gap-2">
          {[0, 120, 240].map((delay) => (
            <div
              key={delay}
              className="w-1.5 h-1.5 bg-stone-700 rounded-full animate-bounce"
              style={{ animationDelay: `${delay}ms` }}
            />
          ))}
        </div>
      ) : (
        <p className="text-stone-800 text-xs">Results appear here</p>
      )}
    </div>
  )
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function Home() {
  const [description, setDescription] = useState('')
  const [rawText, setRawText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  const sections: Record<SectionKey, string> = {
    brief: extractSection(rawText, '## DESIGN BRIEF'),
    materials: extractSection(rawText, '## MATERIALS & DIMENSIONS'),
    vastu: extractSection(rawText, '## VASTU ZONING'),
    midjourney: extractSection(rawText, '## MIDJOURNEY PROMPTS'),
  }

  const hasContent = Object.values(sections).some((s) => s.length > 0)

  // Which section is currently being streamed into
  const activeSection = (() => {
    if (!isLoading) return null
    if (!sections.midjourney) {
      if (!sections.vastu) {
        if (!sections.materials) {
          if (!sections.brief) return 'brief'
          return 'materials'
        }
        return 'vastu'
      }
      return 'midjourney'
    }
    return null
  })()

  const handleGenerate = useCallback(async () => {
    if (!description.trim() || isLoading) return

    // Cancel any in-flight request
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller

    setIsLoading(true)
    setRawText('')
    setError('')

    try {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: description.trim() }),
        signal: controller.signal,
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.error || `HTTP ${res.status}`)
      }

      const reader = res.body!.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value, { stream: true })
        setRawText((prev) => prev + chunk)
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') return
      setError(
        err instanceof Error
          ? err.message
          : 'Generation failed. Check your ANTHROPIC_API_KEY.'
      )
    } finally {
      setIsLoading(false)
    }
  }, [description, isLoading])

  const handleStop = useCallback(() => {
    abortRef.current?.abort()
    setIsLoading(false)
  }, [])

  const copyText = useCallback(async (text: string, key: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(key)
      setTimeout(() => setCopied(null), 2000)
    } catch {
      // clipboard not available
    }
  }, [])

  const copyAllPrompts = useCallback(() => {
    const prompts = sections.midjourney
      .split('\n')
      .filter((l) => l.trim().startsWith('/imagine'))
      .join('\n')
    copyText(prompts, 'all')
  }, [sections.midjourney, copyText])

  return (
    <div className="min-h-screen bg-stone-950 text-stone-100">
      {/* ── Navigation ── */}
      <nav className="sticky top-0 z-10 bg-stone-950/90 backdrop-blur-sm border-b border-stone-800/60 px-6 py-3.5 flex items-center gap-3">
        {/* Logo mark */}
        <div className="w-7 h-7 rounded border border-amber-700/50 flex items-center justify-center shrink-0">
          <div className="w-3 h-3 border border-amber-600/80 rotate-45" />
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-stone-100 font-medium text-sm tracking-tight">
            Vastu Design Generator
          </span>
          <span className="hidden sm:inline text-stone-600 text-xs">
            Architecture AI
          </span>
        </div>
        <div className="ml-auto">
          <span className="text-xs text-stone-700 font-mono">claude-opus-4-6</span>
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
        {/* ── Hero ── */}
        <div className="mb-8">
          <h1 className="text-2xl sm:text-3xl font-light text-stone-100 tracking-tight mb-2">
            Describe your space<span className="text-amber-600">.</span>
          </h1>
          <p className="text-stone-500 text-sm leading-relaxed max-w-xl">
            Get a full design brief, material specifications, Vastu zoning
            analysis, and ready-to-paste Midjourney prompts — instantly.
          </p>
        </div>

        {/* ── Example chips ── */}
        <div className="flex flex-wrap gap-2 mb-4">
          {EXAMPLES.map((ex, i) => (
            <button
              key={i}
              onClick={() => setDescription(ex)}
              className="text-xs px-3 py-1.5 rounded-full border border-stone-800 text-stone-600 hover:border-amber-800/80 hover:text-amber-600/90 transition-colors"
            >
              {ex.length > 48 ? ex.slice(0, 48) + '…' : ex}
            </button>
          ))}
        </div>

        {/* ── Input card ── */}
        <div className="bg-stone-900 border border-stone-800 rounded-xl overflow-hidden mb-5">
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleGenerate()
            }}
            placeholder="e.g. open plan living room, Vastu compliant, earthy tones, exposed concrete ceiling, floor-to-ceiling windows facing north…"
            className="w-full bg-transparent px-5 pt-4 pb-3 text-stone-100 placeholder-stone-700 resize-none h-28 focus:outline-none text-sm leading-relaxed"
          />
          <div className="flex items-center justify-between px-5 py-3 border-t border-stone-800/60">
            <span className="text-stone-700 text-xs hidden sm:block">
              ⌘ Enter to generate
            </span>
            <div className="flex items-center gap-2 ml-auto">
              {isLoading && (
                <button
                  onClick={handleStop}
                  className="px-3 py-1.5 text-xs border border-stone-700 text-stone-500 hover:text-stone-300 rounded-lg transition-colors"
                >
                  Stop
                </button>
              )}
              <button
                onClick={handleGenerate}
                disabled={!description.trim() || isLoading}
                className="flex items-center gap-2 px-5 py-2 bg-amber-700 hover:bg-amber-600 disabled:bg-stone-800 disabled:text-stone-600 text-white text-sm font-medium rounded-lg transition-colors"
              >
                {isLoading ? (
                  <>
                    <span className="w-3.5 h-3.5 border-2 border-white/20 border-t-white/80 rounded-full animate-spin" />
                    Generating…
                  </>
                ) : (
                  'Generate →'
                )}
              </button>
            </div>
          </div>
        </div>

        {/* ── Error ── */}
        {error && (
          <div className="mb-5 px-4 py-3 bg-red-950/50 border border-red-900/70 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* ── Output grid ── */}
        {(hasContent || isLoading) && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 fade-up">
            {SECTIONS.map(({ key, title, emoji, borderClass, dotClass }) => {
              const content = sections[key]
              const isReady = content.length > 0
              const isThisStreaming = activeSection === key

              return (
                <div
                  key={key}
                  className={`bg-stone-900 border rounded-xl overflow-hidden transition-colors duration-500 ${
                    isReady ? borderClass : 'border-stone-800/60'
                  }`}
                >
                  {/* Card header */}
                  <div className="flex items-center justify-between px-5 py-3.5 border-b border-stone-800/60">
                    <div className="flex items-center gap-2">
                      <div
                        className={`w-1.5 h-1.5 rounded-full transition-colors duration-300 ${
                          isReady ? dotClass : 'bg-stone-800'
                        }`}
                      />
                      <span className="text-sm font-medium text-stone-300">
                        {emoji} {title}
                      </span>
                    </div>
                    {key === 'midjourney' && isReady && (
                      <button
                        onClick={copyAllPrompts}
                        className="text-xs text-stone-600 hover:text-stone-400 transition-colors"
                      >
                        {copied === 'all' ? '✓ Copied' : 'Copy all'}
                      </button>
                    )}
                  </div>

                  {/* Card body */}
                  <div className="p-5 min-h-[200px]">
                    {isReady ? (
                      key === 'midjourney' ? (
                        <MidjourneyContent
                          text={content}
                          onCopy={copyText}
                          copied={copied}
                          isStreaming={isThisStreaming}
                        />
                      ) : (
                        <SectionContent
                          text={content}
                          isStreaming={isThisStreaming}
                        />
                      )
                    ) : (
                      <EmptyCard isLoading={isLoading} />
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {/* ── Footer note ── */}
        {hasContent && !isLoading && (
          <p className="text-center text-stone-800 text-xs mt-8">
            Vastu knowledge is advisory — consult a certified Vastu consultant for structural decisions.
          </p>
        )}
      </main>
    </div>
  )
}
