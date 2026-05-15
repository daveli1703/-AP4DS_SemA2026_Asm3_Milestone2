import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import ProductCard from '../components/ProductCard'
import { api } from '../services/api'
import { useWishlist } from '../hooks/useWishlist'
import styles from './HomePage.module.css'

const PAGE_SIZE = 20
const EMPTY_FILTERS = { brand: '', category: '', min_price: '', max_price: '' }

export default function HomePage() {
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q') || ''
  const { items: wishlistItems, toggle, isSaved } = useWishlist()

  const [tab, setTab] = useState('all')
  const [products, setProducts] = useState([])
  const [searchResult, setSearchResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [error, setError] = useState(null)
  const [skip, setSkip] = useState(0)
  const [hasMore, setHasMore] = useState(true)
  const [filters, setFilters] = useState(EMPTY_FILTERS)
  const [activeFilters, setActiveFilters] = useState({})
  const [filterOptions, setFilterOptions] = useState({
    brands: [],
    categories: [],
    price_min: null,
    price_max: null,
  })

  const fetchProducts = useCallback(async (nextSkip, filterParams) => {
    try {
      const data = await api.getProducts(nextSkip, PAGE_SIZE, filterParams)
      if (nextSkip === 0) {
        setProducts(data)
      } else {
        setProducts((prev) => [...prev, ...data])
      }
      setHasMore(data.length === PAGE_SIZE)
      setSkip(nextSkip + data.length)
    } catch {
      setError('Failed to load products. Make sure the backend is running on port 8000.')
    }
  }, [])

  const fetchSearch = useCallback(async (q, filterParams) => {
    try {
      const data = await api.searchProducts(q, filterParams)
      setSearchResult(data)
      setError(null)
    } catch (err) {
      setError(err.status === 422 ? 'Please enter a search term.' : 'Search failed. Make sure the backend is running on port 8000.')
    }
  }, [])

  useEffect(() => {
    api.getProductFilters()
      .then(setFilterOptions)
      .catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    setError(null)
    setSearchResult(null)
    setProducts([])
    setSkip(0)
    setHasMore(true)
    if (query) setTab('all')

    const run = async () => {
      if (query) {
        await fetchSearch(query, activeFilters)
      } else {
        await fetchProducts(0, activeFilters)
      }
      setLoading(false)
    }
    run()
  }, [query, activeFilters, fetchSearch, fetchProducts])

  async function handleLoadMore() {
    setLoadingMore(true)
    await fetchProducts(skip, activeFilters)
    setLoadingMore(false)
  }

  function normalizeFilters(next) {
    let min = next.min_price !== '' ? Number(next.min_price) : undefined
    let max = next.max_price !== '' ? Number(next.max_price) : undefined
    if (Number.isFinite(min) && Number.isFinite(max) && min > max) {
      const swap = min
      min = max
      max = swap
    }
    return {
      brand: next.brand || undefined,
      category: next.category || undefined,
      min_price: Number.isFinite(min) ? min : undefined,
      max_price: Number.isFinite(max) ? max : undefined,
    }
  }

  function handleApplyFilters() {
    setActiveFilters(normalizeFilters(filters))
  }

  function handleResetFilters() {
    setFilters(EMPTY_FILTERS)
    setActiveFilters({})
  }

  const isSearch = Boolean(query)
  const isSavedTab = tab === 'saved' && !isSearch
  const hasActiveFilters = Boolean(
    activeFilters.brand ||
    activeFilters.category ||
    activeFilters.min_price !== undefined ||
    activeFilters.max_price !== undefined
  )

  let displayProducts
  if (isSavedTab) {
    displayProducts = wishlistItems
  } else if (isSearch) {
    displayProducts = searchResult?.results ?? []
  } else {
    displayProducts = products
  }

  return (
    <div className={styles.page}>
      {!isSearch && (
        <section className={styles.hero}>
          <div className={styles.heroInner}>
            <p className={styles.heroEyebrow}>Beauty & Cosmetics</p>
            <h1 className={styles.heroTitle}>
              Discover your<br />
              <em>perfect glow</em>
            </h1>
            <p className={styles.heroSub}>
              Browse thousands of beauty products — from skincare to makeup, all in one place.
            </p>
          </div>
        </section>
      )}

      <div className={styles.container}>
        {isSearch ? (
          <div className={styles.searchHeader}>
            <h2 className={styles.searchTitle}>
              {loading ? 'Searching…' : (
                searchResult
                  ? `${searchResult.count} result${searchResult.count !== 1 ? 's' : ''} for`
                  : 'Results for'
              )}
            </h2>
            {!loading && <p className={styles.searchQuery}>&ldquo;{query}&rdquo;</p>}
            {!loading && searchResult?.count === 0 && (
              <p className={styles.noResults}>
                No products matched your search. Try a different keyword or check your spelling.
              </p>
            )}
          </div>
        ) : (
          <div className={styles.tabBar}>
            <button
              className={`${styles.tab} ${tab === 'all' ? styles.tabActive : ''}`}
              onClick={() => setTab('all')}
            >
              All Products
              {!loading && tab === 'all' && (
                <span className={styles.tabCount}>{products.length}</span>
              )}
            </button>
            <button
              className={`${styles.tab} ${tab === 'saved' ? styles.tabActive : ''}`}
              onClick={() => setTab('saved')}
            >
              Saved
              {wishlistItems.length > 0 && (
                <span className={styles.tabCount}>{wishlistItems.length}</span>
              )}
            </button>
          </div>
        )}

        {!isSavedTab && (
          <section className={styles.filterPanel}>
            <div className={styles.filterHeader}>
              <h3 className={styles.filterTitle}>Filter products</h3>
              {hasActiveFilters && (
                <button className={styles.filterLink} onClick={handleResetFilters}>
                  Clear filters
                </button>
              )}
            </div>
            <div className={styles.filterGrid}>
              <label className={styles.filterGroup}>
                <span className={styles.filterLabel}>Brand</span>
                <select
                  className={styles.filterSelect}
                  value={filters.brand}
                  onChange={(e) => setFilters((prev) => ({ ...prev, brand: e.target.value }))}
                >
                  <option value="">All brands</option>
                  {filterOptions.brands.map((brand) => (
                    <option key={brand} value={brand}>{brand}</option>
                  ))}
                </select>
              </label>

              <label className={styles.filterGroup}>
                <span className={styles.filterLabel}>Category</span>
                <select
                  className={styles.filterSelect}
                  value={filters.category}
                  onChange={(e) => setFilters((prev) => ({ ...prev, category: e.target.value }))}
                >
                  <option value="">All categories</option>
                  {filterOptions.categories.map((category) => (
                    <option key={category} value={category}>{category}</option>
                  ))}
                </select>
              </label>

              <label className={styles.filterGroup}>
                <span className={styles.filterLabel}>Min price</span>
                <input
                  className={styles.filterInput}
                  type="number"
                  min="0"
                  value={filters.min_price}
                  onChange={(e) => setFilters((prev) => ({ ...prev, min_price: e.target.value }))}
                />
              </label>

              <label className={styles.filterGroup}>
                <span className={styles.filterLabel}>Max price</span>
                <input
                  className={styles.filterInput}
                  type="number"
                  min="0"
                  value={filters.max_price}
                  onChange={(e) => setFilters((prev) => ({ ...prev, max_price: e.target.value }))}
                />
              </label>
            </div>
            <div className={styles.filterActions}>
              <button className={styles.filterBtn} onClick={handleResetFilters}>
                Reset
              </button>
              <button className={styles.filterBtnPrimary} onClick={handleApplyFilters}>
                Apply filters
              </button>
            </div>
          </section>
        )}

        {error && (
          <div className={styles.error}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            {error}
          </div>
        )}

        {isSavedTab ? (
          wishlistItems.length === 0 ? (
            <div className={styles.emptyWishlist}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
              </svg>
              <p>Your wishlist is empty.</p>
              <p className={styles.emptyWishlistSub}>
                Browse products and tap the heart icon to save them here.
              </p>
            </div>
          ) : (
            <div className={styles.grid}>
              {displayProducts.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  saved={isSaved(product.id)}
                  onToggleWishlist={toggle}
                />
              ))}
            </div>
          )
        ) : loading ? (
          <div className={styles.grid}>
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className={styles.skeleton} />
            ))}
          </div>
        ) : displayProducts.length > 0 ? (
          <>
            <div className={styles.grid}>
              {displayProducts.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  saved={isSaved(product.id)}
                  onToggleWishlist={toggle}
                />
              ))}
            </div>
            {!isSearch && hasMore && (
              <div className={styles.loadMoreWrap}>
                <button
                  className={styles.loadMoreBtn}
                  onClick={handleLoadMore}
                  disabled={loadingMore}
                >
                  {loadingMore ? 'Loading…' : 'Load more products'}
                </button>
              </div>
            )}
          </>
        ) : !error ? null : null}
      </div>
    </div>
  )
}
