import { useState, useEffect, useRef } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import styles from './Header.module.css'

export default function Header() {
  const [searchParams] = useSearchParams()
  const [query, setQuery] = useState(searchParams.get('q') || '')
  const navigate = useNavigate()
  const inputRef = useRef(null)

  useEffect(() => {
    setQuery(searchParams.get('q') || '')
  }, [searchParams])

  function handleSubmit(e) {
    e.preventDefault()
    const trimmed = query.trim()
    if (trimmed) {
      navigate(`/?q=${encodeURIComponent(trimmed)}`)
    } else {
      navigate('/')
    }
  }

  function handleClear() {
    setQuery('')
    navigate('/')
    inputRef.current?.focus()
  }

  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <Link to="/" className={styles.logo}>
          <span className={styles.logoGlow}>GL</span>
          <span className={styles.logoBar}>Ō</span>
          <span className={styles.logoGlow}>W</span>
        </Link>

        <form className={styles.searchForm} onSubmit={handleSubmit} role="search">
          <div className={styles.searchWrap}>
            <svg className={styles.searchIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
              <circle cx="10.5" cy="10.5" r="6.5" />
              <line x1="15.5" y1="15.5" x2="21" y2="21" />
            </svg>
            <input
              ref={inputRef}
              className={styles.searchInput}
              type="search"
              placeholder="Search brands, products…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              aria-label="Search products"
            />
            {query && (
              <button
                type="button"
                className={styles.clearBtn}
                onClick={handleClear}
                aria-label="Clear search"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            )}
          </div>
          <button className={styles.searchBtn} type="submit">Search</button>
        </form>

        <nav className={styles.nav}>
          <Link to="/" className={styles.navLink}>Products</Link>
        </nav>
      </div>
    </header>
  )
}
