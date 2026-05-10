'use client'

import { useState, useEffect, useRef, useCallback } from 'react'

// ─── Types ────────────────────────────────────────────────────────────────────

interface Product {
  id: number
  name: string
  tagline: string
  price: string
  material: string
  image: string
  badge: string | null
  bg: string
}

interface Material {
  name: string
  short: string
  origin: string
  character: string
  description: string
  properties: string[]
  image: string
  accent: string
}

// ─── Data ─────────────────────────────────────────────────────────────────────

const PRODUCTS: Product[] = [
  {
    id: 1,
    name: 'Lune Sofa',
    tagline: 'Serenity in every curve',
    price: '$2,890',
    material: 'Full-grain leather · Solid beech frame',
    image: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&q=80&auto=format&fit=crop',
    badge: 'New',
    bg: '#f0ece4',
  },
  {
    id: 2,
    name: 'Arc Lounge Chair',
    tagline: 'Redefining comfort',
    price: '$890',
    material: 'Bouclé fabric · Solid walnut legs',
    image: 'https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?w=800&q=80&auto=format&fit=crop',
    badge: null,
    bg: '#ede8e0',
  },
  {
    id: 3,
    name: 'Mesa Dining Table',
    tagline: 'Where stories gather',
    price: '$1,650',
    material: 'American white oak · Oiled finish',
    image: 'https://images.unsplash.com/photo-1449247709967-d4461a6a6103?w=800&q=80&auto=format&fit=crop',
    badge: 'Bestseller',
    bg: '#e8e3d9',
  },
  {
    id: 4,
    name: 'Nox Bed Frame',
    tagline: 'Sleep in quiet luxury',
    price: '$1,200',
    material: 'Smoked walnut · Platform design',
    image: 'https://images.unsplash.com/photo-1505693314120-0d443867891c?w=800&q=80&auto=format&fit=crop',
    badge: null,
    bg: '#e4dfd6',
  },
  {
    id: 5,
    name: 'Koto Shelf System',
    tagline: 'Order, beautifully imposed',
    price: '$680',
    material: 'Black powder steel · Tempered glass',
    image: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80&auto=format&fit=crop',
    badge: null,
    bg: '#e0dbd2',
  },
  {
    id: 6,
    name: 'Cirro Coffee Table',
    tagline: 'Marble meets moment',
    price: '$1,100',
    material: 'Carrara marble · Brushed brass legs',
    image: 'https://images.unsplash.com/photo-1567016432779-094069958ea5?w=800&q=80&auto=format&fit=crop',
    badge: 'Limited',
    bg: '#f0ece6',
  },
]

const MATERIALS: Material[] = [
  {
    name: 'American White Oak',
    short: 'Oak',
    origin: 'North America',
    character: 'Warm · Natural grain · Timeless',
    description:
      'Sustainably sourced from managed forests, our white oak offers exceptional strength with a naturally beautiful grain. Each piece is quarter-sawn for stability and finished with hand-rubbed oil that lets the wood breathe and develop character over decades.',
    properties: ['Hardness: 1,360 lbf', 'Grain: Straight to wavy', 'Color: Golden wheat', 'Finish: Hand-rubbed oil'],
    image: 'https://images.unsplash.com/photo-1541123437-3a3da8dfd4e3?w=900&q=80&auto=format&fit=crop',
    accent: '#c8a97e',
  },
  {
    name: 'Italian Full-Grain Leather',
    short: 'Leather',
    origin: 'Tuscany, Italy',
    character: 'Ages beautifully · Supple · Rich',
    description:
      "Sourced from Tuscan tanneries using traditional vegetable-tanning methods, our full-grain leather retains the natural surface of the hide. It develops a rich, deep patina over time — becoming more beautiful with every year of use.",
    properties: ['Thickness: 2.5 mm', 'Tanning: Vegetable', 'Origin: Tuscany', 'Finish: Natural wax'],
    image: 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=900&q=80&auto=format&fit=crop',
    accent: '#8b6f47',
  },
  {
    name: 'Carrara Marble',
    short: 'Marble',
    origin: 'Tuscany, Italy',
    character: 'Unique veining · Eternal · Cool',
    description:
      'Quarried from the mountains of Carrara, each slab is unique — a geological fingerprint millions of years in the making. The subtle grey veining against white gives our tables a quiet drama that no synthetic surface can replicate.',
    properties: ['Origin: Carrara, Italy', 'Finish: Honed matte', 'Seal: Nano-protection', 'Veining: Grey on white'],
    image: 'https://images.unsplash.com/photo-1518893494013-481c1d8ed3fd?w=900&q=80&auto=format&fit=crop',
    accent: '#9e9e9e',
  },
  {
    name: 'Brushed Brass',
    short: 'Brass',
    origin: 'Hand-finished',
    character: 'Warm tone · Ages gracefully · Luxe',
    description:
      'Our solid brass components are hand-finished with a satin brush to soften the metallic sheen into something warmer, more intimate. No lacquer means the brass ages naturally, developing a living patina that reflects the passage of time.',
    properties: ['Alloy: 70/30 Cu/Zn', 'Finish: Hand-brushed', 'Lacquer: None', 'Patina: Natural'],
    image: 'https://images.unsplash.com/photo-1547949003-9792a18a2601?w=900&q=80&auto=format&fit=crop',
    accent: '#b5973d',
  },
  {
    name: 'Bouclé Fabric',
    short: 'Bouclé',
    origin: 'European looms',
    character: 'Soft texture · Durable · Modern',
    description:
      "Woven on traditional European looms, our bouclé is a looped textile that creates a subtly textured, deeply tactile surface. It's extraordinarily soft to the touch, built to withstand decades of daily use, and visually rich without ever being loud.",
    properties: ['Composition: Wool blend', 'Rub test: 80,000+', 'Width: 140 cm', 'Weight: 450 g/m²'],
    image: 'https://images.unsplash.com/photo-1584464491033-06628f3a6b7b?w=900&q=80&auto=format&fit=crop',
    accent: '#c4b89a',
  },
]

// ─── Hooks ────────────────────────────────────────────────────────────────────

function useInView(threshold = 0.12) {
  const ref = useRef<HTMLDivElement>(null)
  const [inView, setInView] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true)
          observer.unobserve(entry.target)
        }
      },
      { threshold }
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [threshold])

  return [ref, inView] as const
}

// ─── Reveal wrapper (scroll-triggered fade-up) ────────────────────────────────

function Reveal({
  children,
  delay = 0,
  className = '',
}: {
  children: React.ReactNode
  delay?: number
  className?: string
}) {
  const [ref, inView] = useInView()
  return (
    <div
      ref={ref}
      className={className}
      style={{
        opacity: inView ? 1 : 0,
        transform: inView ? 'translateY(0)' : 'translateY(28px)',
        transition: `opacity 0.9s cubic-bezier(0.22,1,0.36,1) ${delay}s, transform 0.9s cubic-bezier(0.22,1,0.36,1) ${delay}s`,
      }}
    >
      {children}
    </div>
  )
}

// ─── Product Card ─────────────────────────────────────────────────────────────

function ProductCard({ product, index }: { product: Product; index: number }) {
  const [hovered, setHovered] = useState(false)

  return (
    <Reveal delay={index * 0.08}>
      <div
        className="cursor-pointer"
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
      >
        <div
          className="relative overflow-hidden rounded-3xl mb-5"
          style={{ backgroundColor: product.bg, aspectRatio: '4/5' }}
        >
          {product.badge && (
            <span className="absolute top-4 left-4 z-10 text-xs font-medium bg-white text-zinc-800 px-3 py-1.5 rounded-full">
              {product.badge}
            </span>
          )}

          <img
            src={product.image}
            alt={product.name}
            loading="lazy"
            className="w-full h-full object-cover"
            style={{
              transform: hovered ? 'scale(1.06)' : 'scale(1)',
              transition: 'transform 0.9s cubic-bezier(0.25,0.46,0.45,0.94)',
            }}
          />

          <div
            className="absolute inset-0 flex items-end p-6"
            style={{
              background: 'linear-gradient(to top, rgba(0,0,0,0.45) 0%, transparent 55%)',
              opacity: hovered ? 1 : 0,
              transition: 'opacity 0.4s ease',
            }}
          >
            <button
              className="w-full bg-white text-zinc-900 text-sm font-medium py-3.5 rounded-2xl"
              style={{ transition: 'transform 0.3s ease', transform: hovered ? 'translateY(0)' : 'translateY(8px)' }}
            >
              View Details →
            </button>
          </div>
        </div>

        <div className="px-1">
          <div className="flex items-start justify-between mb-1">
            <h3 className="font-medium text-zinc-900 text-[15px]">{product.name}</h3>
            <span className="font-medium text-zinc-900 text-[15px] ml-4 shrink-0">{product.price}</span>
          </div>
          <p className="text-sm text-zinc-500 mb-1">{product.tagline}</p>
          <p className="text-xs text-zinc-400">{product.material}</p>
        </div>
      </div>
    </Reveal>
  )
}

// ─── Navbar ───────────────────────────────────────────────────────────────────

function Navbar() {
  const navRef = useRef<HTMLElement>(null)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    const handler = () => {
      if (!navRef.current) return
      const scrolled = window.scrollY > 60
      navRef.current.style.backgroundColor = scrolled ? 'rgba(255,255,255,0.88)' : 'transparent'
      navRef.current.style.backdropFilter = scrolled ? 'blur(20px) saturate(180%)' : 'none'
      ;(navRef.current.style as CSSStyleDeclaration & { webkitBackdropFilter: string }).webkitBackdropFilter = scrolled ? 'blur(20px) saturate(180%)' : 'none'
      navRef.current.style.borderBottom = scrolled ? '1px solid rgba(0,0,0,0.07)' : '1px solid transparent'
    }
    window.addEventListener('scroll', handler, { passive: true })
    return () => window.removeEventListener('scroll', handler)
  }, [])

  return (
    <nav
      ref={navRef}
      className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 py-5"
      style={{ transition: 'background-color 0.4s ease, backdrop-filter 0.4s ease, border-color 0.4s ease' }}
    >
      <a href="#" className="text-xl font-semibold tracking-tight text-white" style={{ letterSpacing: '-0.03em' }}>
        FORMA
      </a>

      {/* Desktop links */}
      <div className="hidden md:flex items-center gap-8">
        {['Products', 'Materials', 'Craftsmanship', 'About'].map((link) => (
          <a
            key={link}
            href={`#${link.toLowerCase()}`}
            className="text-sm text-white/80 hover:text-white transition-colors"
          >
            {link}
          </a>
        ))}
        <a
          href="#products"
          className="ml-2 bg-white text-zinc-900 px-5 py-2 rounded-full text-sm font-medium hover:bg-zinc-100 transition-colors"
        >
          Shop Now
        </a>
      </div>

      {/* Mobile menu button */}
      <button
        className="md:hidden text-white p-2"
        onClick={() => setMenuOpen((v) => !v)}
        aria-label="Toggle menu"
      >
        <div className="w-6 flex flex-col gap-1.5">
          <span
            className="block h-px bg-white transition-all"
            style={{ transform: menuOpen ? 'rotate(45deg) translateY(5px)' : 'none' }}
          />
          <span
            className="block h-px bg-white transition-all"
            style={{ opacity: menuOpen ? 0 : 1 }}
          />
          <span
            className="block h-px bg-white transition-all"
            style={{ transform: menuOpen ? 'rotate(-45deg) translateY(-5px)' : 'none' }}
          />
        </div>
      </button>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="absolute top-full left-0 right-0 bg-white/95 backdrop-blur-xl border-b border-zinc-200 md:hidden">
          {['Products', 'Materials', 'Craftsmanship', 'About'].map((link) => (
            <a
              key={link}
              href={`#${link.toLowerCase()}`}
              className="block px-8 py-4 text-zinc-900 text-sm border-b border-zinc-100 hover:bg-zinc-50 transition-colors"
              onClick={() => setMenuOpen(false)}
            >
              {link}
            </a>
          ))}
          <div className="px-8 py-5">
            <a href="#products" className="block text-center bg-zinc-900 text-white py-3 rounded-full text-sm font-medium">
              Shop Now
            </a>
          </div>
        </div>
      )}
    </nav>
  )
}

// ─── Hero ─────────────────────────────────────────────────────────────────────

function Hero() {
  const imgRef = useRef<HTMLImageElement>(null)

  useEffect(() => {
    const handler = () => {
      if (imgRef.current) {
        imgRef.current.style.transform = `scale(1.08) translateY(${window.scrollY * 0.25}px)`
      }
    }
    window.addEventListener('scroll', handler, { passive: true })
    return () => window.removeEventListener('scroll', handler)
  }, [])

  return (
    <section className="relative h-screen flex items-center justify-center overflow-hidden">
      {/* Parallax background */}
      <img
        ref={imgRef}
        src="https://images.unsplash.com/photo-1586023492125-27b2c045efd3?w=1800&q=85&auto=format&fit=crop"
        alt=""
        aria-hidden
        className="absolute inset-0 w-full h-full object-cover"
        style={{ transform: 'scale(1.08)', transformOrigin: 'center center', transition: 'none' }}
      />

      {/* Gradient overlays */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-black/25 to-black/65" />
      <div className="absolute inset-0 bg-gradient-to-r from-black/20 to-transparent" />

      {/* Content */}
      <div className="relative z-10 text-center px-6 max-w-5xl mx-auto">
        <p
          className="hero-word text-white/70 text-xs font-medium tracking-[0.25em] uppercase mb-8"
          style={{ animationDelay: '0.05s' }}
        >
          New Collection · 2025
        </p>

        <h1
          className="text-white font-light leading-[1.02] mb-8 tracking-tight"
          style={{ fontSize: 'clamp(52px, 9vw, 108px)', letterSpacing: '-0.04em' }}
        >
          <span className="hero-word block" style={{ animationDelay: '0.15s' }}>Furniture for</span>
          <span className="hero-word block" style={{ animationDelay: '0.32s' }}>the way you live.</span>
        </h1>

        <p
          className="hero-sub text-white/70 text-lg md:text-xl font-light mb-12 max-w-md mx-auto leading-relaxed"
          style={{ animationDelay: '0.52s', letterSpacing: '-0.01em' }}
        >
          Crafted from the world's finest materials. Designed to endure.
        </p>

        <div className="hero-cta flex flex-col sm:flex-row items-center justify-center gap-4" style={{ animationDelay: '0.72s' }}>
          <a
            href="#products"
            className="inline-flex items-center gap-2 bg-white text-zinc-900 px-8 py-4 rounded-full text-sm font-medium hover:bg-zinc-50 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            Explore Collection
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M7 1L13 7L7 13M13 7H1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </a>
          <a
            href="#video"
            className="inline-flex items-center gap-2 text-white/80 text-sm font-medium hover:text-white transition-colors px-4 py-4"
          >
            <span className="w-8 h-8 rounded-full border border-white/40 flex items-center justify-center">
              <svg width="10" height="11" viewBox="0 0 10 11" fill="currentColor">
                <path d="M2 1.5L8.5 5.5L2 9.5V1.5Z"/>
              </svg>
            </span>
            Watch our story
          </a>
        </div>
      </div>

      {/* Scroll indicator */}
      <div
        className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
        style={{ animation: 'fadeIn 1s ease 1.4s both' }}
      >
        <p className="text-white/40 text-[10px] tracking-widest uppercase">Scroll</p>
        <div className="w-px h-12 bg-white/30 scroll-line" />
      </div>
    </section>
  )
}

// ─── Intro strip ──────────────────────────────────────────────────────────────

function IntroStrip() {
  return (
    <section className="py-28 px-8 bg-zinc-50">
      <Reveal>
        <p
          className="text-2xl md:text-3xl font-light text-zinc-500 max-w-4xl mx-auto text-center leading-relaxed"
          style={{ letterSpacing: '-0.015em' }}
        >
          At FORMA, we believe furniture should be{' '}
          <span className="text-zinc-900">both sculpture and function</span> — pieces that make
          a room feel complete the moment they arrive, and{' '}
          <span className="text-zinc-900">better every year they remain</span>.
        </p>
      </Reveal>
    </section>
  )
}

// ─── Products grid ────────────────────────────────────────────────────────────

function ProductsSection() {
  return (
    <section id="products" className="py-28 px-8 max-w-7xl mx-auto">
      <Reveal>
        <div className="mb-20">
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-[0.18em] mb-4">Collection</p>
          <h2 className="text-5xl md:text-6xl font-light text-zinc-900" style={{ letterSpacing: '-0.04em' }}>
            New arrivals
          </h2>
        </div>
      </Reveal>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-16">
        {PRODUCTS.map((product, i) => (
          <ProductCard key={product.id} product={product} index={i} />
        ))}
      </div>

      <Reveal delay={0.2}>
        <div className="mt-16 text-center">
          <a
            href="#"
            className="inline-flex items-center gap-2 text-sm font-medium text-zinc-900 border border-zinc-300 px-8 py-3.5 rounded-full hover:bg-zinc-900 hover:text-white hover:border-zinc-900 transition-all"
          >
            View all 42 pieces
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M7 1L13 7L7 13M13 7H1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </a>
        </div>
      </Reveal>
    </section>
  )
}

// ─── Video section ────────────────────────────────────────────────────────────

function VideoSection() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const sectionRef = useRef<HTMLElement>(null)
  const [playing, setPlaying] = useState(true)

  const togglePlay = useCallback(() => {
    const v = videoRef.current
    if (!v) return
    if (v.paused) { v.play(); setPlaying(true) }
    else { v.pause(); setPlaying(false) }
  }, [])

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (videoRef.current) {
          if (entry.isIntersecting) videoRef.current.play().catch(() => {})
          else videoRef.current.pause()
        }
      },
      { threshold: 0.3 }
    )
    if (sectionRef.current) observer.observe(sectionRef.current)
    return () => observer.disconnect()
  }, [])

  return (
    <section id="video" ref={sectionRef} className="relative h-screen overflow-hidden">
      <video
        ref={videoRef}
        className="w-full h-full object-cover"
        autoPlay
        muted
        loop
        playsInline
        poster="https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=1600&q=85&auto=format&fit=crop"
      >
        <source
          src="https://videos.pexels.com/video-files/3209828/3209828-hd_1280_720_25fps.mp4"
          type="video/mp4"
        />
        <source
          src="https://videos.pexels.com/video-files/7579430/7579430-hd_1280_720_30fps.mp4"
          type="video/mp4"
        />
      </video>

      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-black/65 via-black/30 to-transparent" />
      <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent" />

      {/* Text */}
      <div className="absolute inset-0 flex items-center">
        <div className="px-8 md:px-20 max-w-2xl">
          <Reveal>
            <p className="text-white/50 text-xs font-medium uppercase tracking-[0.2em] mb-6">Our Process</p>
            <h2
              className="text-white font-light leading-[1.05] mb-8"
              style={{ fontSize: 'clamp(36px, 5vw, 64px)', letterSpacing: '-0.04em' }}
            >
              Crafted to last<br />a lifetime.
            </h2>
            <p className="text-white/65 text-lg font-light leading-relaxed mb-10 max-w-sm">
              Every piece is built by hand in our workshops, where master craftspeople apply techniques passed down across generations.
            </p>
            <a
              href="#"
              className="inline-flex items-center gap-2 text-white text-sm font-medium border border-white/35 px-7 py-3.5 rounded-full hover:bg-white/10 transition-colors"
            >
              Our Craftsmanship
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M7 1L13 7L7 13M13 7H1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </a>
          </Reveal>
        </div>
      </div>

      {/* Play/pause control */}
      <button
        onClick={togglePlay}
        className="absolute bottom-8 right-8 w-12 h-12 rounded-full border border-white/30 bg-black/20 backdrop-blur-sm flex items-center justify-center text-white hover:bg-black/40 transition-colors"
        aria-label={playing ? 'Pause video' : 'Play video'}
      >
        {playing ? (
          <svg width="12" height="14" viewBox="0 0 12 14" fill="currentColor">
            <rect x="0" y="0" width="4" height="14" rx="1"/>
            <rect x="8" y="0" width="4" height="14" rx="1"/>
          </svg>
        ) : (
          <svg width="12" height="14" viewBox="0 0 12 14" fill="currentColor">
            <path d="M0 1L12 7L0 13V1Z"/>
          </svg>
        )}
      </button>
    </section>
  )
}

// ─── Materials ────────────────────────────────────────────────────────────────

function MaterialsSection() {
  const [active, setActive] = useState(0)
  const [prevActive, setPrevActive] = useState(0)
  const material = MATERIALS[active]

  const switchMaterial = useCallback((i: number) => {
    setPrevActive(active)
    setActive(i)
  }, [active])

  return (
    <section id="materials" className="py-28 bg-zinc-50">
      <div className="max-w-7xl mx-auto px-8">
        <Reveal>
          <div className="mb-20">
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-[0.18em] mb-4">What we use</p>
            <h2 className="text-5xl md:text-6xl font-light text-zinc-900" style={{ letterSpacing: '-0.04em' }}>
              Materials
            </h2>
          </div>
        </Reveal>

        {/* Tabs */}
        <div className="flex flex-wrap gap-2.5 mb-14">
          {MATERIALS.map((m, i) => (
            <button
              key={m.short}
              onClick={() => switchMaterial(i)}
              className="px-5 py-2.5 rounded-full text-sm font-medium transition-all duration-300"
              style={{
                backgroundColor: active === i ? '#1d1d1f' : 'white',
                color: active === i ? 'white' : '#6e6e73',
                border: `1px solid ${active === i ? '#1d1d1f' : '#d4d4d8'}`,
                transform: active === i ? 'scale(1.02)' : 'scale(1)',
              }}
            >
              {m.short}
            </button>
          ))}
        </div>

        {/* Panel */}
        <div key={active} className="material-panel grid grid-cols-1 lg:grid-cols-2 gap-14 items-center">
          {/* Image */}
          <div className="relative rounded-3xl overflow-hidden aspect-square">
            <img
              src={material.image}
              alt={material.name}
              loading="lazy"
              className="w-full h-full object-cover"
            />
            {/* Color swatch */}
            <div
              className="absolute bottom-5 left-5 w-10 h-10 rounded-full border-2 border-white shadow-lg"
              style={{ backgroundColor: material.accent }}
            />
            {/* Origin badge */}
            <div className="absolute top-5 right-5 bg-black/60 backdrop-blur-sm text-white text-xs px-3 py-1.5 rounded-full">
              {material.origin}
            </div>
          </div>

          {/* Details */}
          <div>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-[0.18em] mb-4">{material.origin}</p>
            <h3
              className="text-4xl md:text-5xl font-light text-zinc-900 mb-3"
              style={{ letterSpacing: '-0.03em' }}
            >
              {material.name}
            </h3>
            <p
              className="text-sm font-medium mb-8"
              style={{ color: material.accent }}
            >
              {material.character}
            </p>
            <p className="text-zinc-500 leading-relaxed text-[15px] mb-10 max-w-md">
              {material.description}
            </p>

            {/* Properties grid */}
            <div className="grid grid-cols-2 gap-3">
              {material.properties.map((prop) => {
                const colonIdx = prop.indexOf(': ')
                const key = prop.slice(0, colonIdx)
                const val = prop.slice(colonIdx + 2)
                return (
                  <div key={prop} className="bg-white rounded-2xl p-4">
                    <p className="text-[11px] text-zinc-400 uppercase tracking-wider mb-1.5">{key}</p>
                    <p className="text-sm font-medium text-zinc-800">{val}</p>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

// ─── Featured pieces ──────────────────────────────────────────────────────────

function FeaturedSection() {
  const items = [
    {
      tag: 'New · Seating',
      name: 'Lune Sofa',
      description:
        'Named for its gentle arc, the Lune is built around a single principle: total comfort without compromising form. Available in six leather tones and three solid wood base finishes.',
      detail: 'Full-grain leather · Solid beech · Made in Italy',
      price: '$2,890',
      image: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=1000&q=85&auto=format&fit=crop',
      bg: '#f0ece4',
      reversed: false,
    },
    {
      tag: 'Bestseller · Dining',
      name: 'Mesa Dining Table',
      description:
        'A single plank of American white oak, oiled to let the grain speak for itself. The Mesa seats eight and becomes the anchor of any dining room — quietly confident, endlessly present.',
      detail: 'American white oak · Hand-oiled · Portland workshop',
      price: '$1,650',
      image: 'https://images.unsplash.com/photo-1449247709967-d4461a6a6103?w=1000&q=85&auto=format&fit=crop',
      bg: '#e8e3d9',
      reversed: true,
    },
  ]

  return (
    <section id="craftsmanship" className="py-28 max-w-7xl mx-auto px-8">
      <Reveal>
        <div className="mb-20">
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-[0.18em] mb-4">Spotlight</p>
          <h2 className="text-5xl md:text-6xl font-light text-zinc-900" style={{ letterSpacing: '-0.04em' }}>
            Featured pieces
          </h2>
        </div>
      </Reveal>

      {items.map((item, i) => (
        <Reveal key={item.name} delay={0.05}>
          <div
            className={`grid grid-cols-1 lg:grid-cols-2 gap-16 items-center ${i < items.length - 1 ? 'mb-36' : ''}`}
          >
            <div className={item.reversed ? 'lg:order-2' : ''}>
              <div
                className="rounded-3xl overflow-hidden aspect-square"
                style={{ backgroundColor: item.bg }}
              >
                <img
                  src={item.image}
                  alt={item.name}
                  loading="lazy"
                  className="w-full h-full object-cover hover:scale-[1.04] transition-transform duration-1000"
                />
              </div>
            </div>

            <div className={item.reversed ? 'lg:order-1' : ''}>
              <p className="text-xs font-medium text-zinc-400 uppercase tracking-[0.18em] mb-5">{item.tag}</p>
              <h3
                className="text-5xl font-light text-zinc-900 mb-5"
                style={{ letterSpacing: '-0.04em', lineHeight: 1.05 }}
              >
                {item.name}
              </h3>
              <p className="text-zinc-500 leading-relaxed mb-6 text-[16px] max-w-md">
                {item.description}
              </p>
              <p className="text-zinc-400 text-sm mb-10">{item.detail}</p>
              <div className="flex items-center gap-7">
                <span className="text-3xl font-light text-zinc-900" style={{ letterSpacing: '-0.02em' }}>
                  {item.price}
                </span>
                <a
                  href="#"
                  className="bg-zinc-900 text-white px-8 py-3.5 rounded-full text-sm font-medium hover:bg-zinc-700 transition-colors"
                >
                  Shop Now
                </a>
                <a href="#" className="text-sm text-zinc-500 hover:text-zinc-900 transition-colors underline underline-offset-4">
                  Learn more
                </a>
              </div>
            </div>
          </div>
        </Reveal>
      ))}
    </section>
  )
}

// ─── Stats strip ──────────────────────────────────────────────────────────────

function StatsSection() {
  const stats = [
    { value: '12', label: 'Years of craft' },
    { value: '200+', label: 'Unique pieces' },
    { value: '40+', label: 'Countries shipped' },
    { value: '100%', label: 'Sustainably sourced' },
  ]

  return (
    <section className="py-24 bg-zinc-900 text-white">
      <div className="max-w-7xl mx-auto px-8">
        <Reveal>
          <p className="text-center text-zinc-500 text-xs font-medium uppercase tracking-[0.2em] mb-16">
            By the numbers
          </p>
        </Reveal>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-12 text-center">
          {stats.map(({ value, label }, i) => (
            <Reveal key={label} delay={i * 0.09}>
              <div>
                <p className="text-5xl md:text-6xl font-light mb-3" style={{ letterSpacing: '-0.04em' }}>
                  {value}
                </p>
                <p className="text-zinc-500 text-sm">{label}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}

// ─── CTA Banner ───────────────────────────────────────────────────────────────

function CTABanner() {
  return (
    <section className="relative overflow-hidden py-32 px-8">
      <img
        src="https://images.unsplash.com/photo-1567016432779-094069958ea5?w=1400&q=80&auto=format&fit=crop"
        alt=""
        aria-hidden
        className="absolute inset-0 w-full h-full object-cover"
      />
      <div className="absolute inset-0 bg-black/55" />

      <div className="relative z-10 text-center max-w-2xl mx-auto">
        <Reveal>
          <h2
            className="text-white font-light mb-6"
            style={{ fontSize: 'clamp(36px, 5vw, 60px)', letterSpacing: '-0.04em' }}
          >
            Start with one perfect piece.
          </h2>
          <p className="text-white/65 text-lg font-light mb-10 leading-relaxed">
            Every home begins with a single decision. Let us help you make the right one.
          </p>
          <a
            href="#products"
            className="inline-flex items-center gap-2 bg-white text-zinc-900 px-10 py-4 rounded-full text-sm font-medium hover:bg-zinc-100 transition-all hover:scale-[1.02]"
          >
            Browse the Collection
          </a>
        </Reveal>
      </div>
    </section>
  )
}

// ─── Footer ───────────────────────────────────────────────────────────────────

function Footer() {
  const columns = [
    {
      title: 'Products',
      links: ['New Arrivals', 'Seating', 'Tables', 'Beds & Frames', 'Storage', 'Accessories'],
    },
    {
      title: 'Company',
      links: ['About FORMA', 'Craftsmanship', 'Sustainability', 'Careers', 'Press'],
    },
    {
      title: 'Support',
      links: ['Contact Us', 'Care Guide', 'Delivery', 'Returns', 'Warranty', 'Trade Program'],
    },
  ]

  return (
    <footer className="bg-zinc-900 text-white pt-20 pb-10">
      <div className="max-w-7xl mx-auto px-8">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-12 mb-20">
          <div className="lg:col-span-2">
            <p className="text-2xl font-semibold tracking-tight mb-5" style={{ letterSpacing: '-0.03em' }}>
              FORMA
            </p>
            <p className="text-zinc-400 text-sm leading-relaxed max-w-xs mb-8">
              Furniture designed to last. Crafted with care. Every piece we make is a commitment to quality, beauty, and conscious production.
            </p>
            {/* Social icons */}
            <div className="flex gap-4">
              {['Instagram', 'Pinterest', 'LinkedIn'].map((social) => (
                <a
                  key={social}
                  href="#"
                  className="w-9 h-9 rounded-full border border-white/15 flex items-center justify-center text-zinc-500 hover:text-white hover:border-white/40 transition-colors text-xs"
                  aria-label={social}
                >
                  {social[0]}
                </a>
              ))}
            </div>
          </div>

          {columns.map(({ title, links }) => (
            <div key={title}>
              <p className="text-[10px] font-medium text-zinc-500 uppercase tracking-[0.2em] mb-5">{title}</p>
              <ul className="space-y-3">
                {links.map((link) => (
                  <li key={link}>
                    <a href="#" className="text-zinc-400 text-sm hover:text-white transition-colors">
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Newsletter */}
        <div className="border-t border-white/8 pt-10 mb-10">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div>
              <p className="text-sm font-medium mb-1">Stay in the know</p>
              <p className="text-zinc-500 text-sm">New pieces, stories, and invitations to our showrooms.</p>
            </div>
            <div className="flex gap-3 w-full md:w-auto">
              <input
                type="email"
                placeholder="your@email.com"
                className="bg-white/8 border border-white/12 text-white placeholder-zinc-600 text-sm px-5 py-3 rounded-full flex-1 md:w-64 focus:outline-none focus:border-white/30 transition-colors"
              />
              <button className="bg-white text-zinc-900 px-6 py-3 rounded-full text-sm font-medium hover:bg-zinc-100 transition-colors shrink-0">
                Subscribe
              </button>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="border-t border-white/8 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-zinc-600 text-xs">© 2025 FORMA Studio, Inc. All rights reserved.</p>
          <div className="flex gap-6">
            {['Privacy Policy', 'Terms of Service', 'Cookie Settings'].map((item) => (
              <a key={item} href="#" className="text-zinc-600 text-xs hover:text-zinc-400 transition-colors">
                {item}
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  )
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function FormaPage() {
  return (
    <div className="bg-white text-zinc-900">
      <Navbar />
      <Hero />
      <IntroStrip />
      <ProductsSection />
      <VideoSection />
      <MaterialsSection />
      <FeaturedSection />
      <StatsSection />
      <CTABanner />
      <Footer />
    </div>
  )
}
