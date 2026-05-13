import { useState, useEffect, useCallback } from 'react'
import ReviewCard from './ReviewCard'
import ReviewForm from './ReviewForm'
import { api } from '../services/api'
import styles from './ReviewList.module.css'

const PAGE_SIZE = 6

export default function ReviewList({ productId, onReviewAdded }) {
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [sort, setSort] = useState('newest')
  const [skip, setSkip] = useState(0)
  const [hasMore, setHasMore] = useState(true)

  const loadPage = useCallback(async (nextSkip, replace = false) => {
    try {
      const data = await api.getReviews(productId, {
        sort,
        skip: nextSkip,
        limit: PAGE_SIZE,
      })
      if (replace) {
        setReviews(data)
      } else {
        setReviews((prev) => [...prev, ...data])
      }
      setHasMore(data.length === PAGE_SIZE)
      setSkip(nextSkip + data.length)
    } catch {
      if (replace) setReviews([])
      setHasMore(false)
    } finally {
      if (replace) setLoading(false)
    }
  }, [productId, sort])

  useEffect(() => {
    setLoading(true)
    setReviews([])
    setSkip(0)
    setHasMore(true)
    loadPage(0, true)
  }, [productId, sort, loadPage])

  function handleReviewAdded(newReview) {
    setShowForm(false)
    setLoading(true)
    loadPage(0, true)
    onReviewAdded?.(newReview)
  }

  async function handleLoadMore() {
    if (loadingMore || !hasMore) return
    setLoadingMore(true)
    await loadPage(skip, false)
    setLoadingMore(false)
  }

  const avgRating = reviews.length
    ? (reviews.reduce((s, r) => s + r.rating, 0) / reviews.length).toFixed(1)
    : null

  return (
    <section className={styles.section}>
      <div className={styles.sectionHeader}>
        <div className={styles.titleRow}>
          <h2 className={styles.title}>
            Reviews
            {!loading && reviews.length > 0 && (
              <span className={styles.count}>{reviews.length}</span>
            )}
          </h2>
          {avgRating && (
            <span className={styles.avgRating}>
              <span className={styles.avgStar}>★</span> {avgRating} avg
            </span>
          )}
        </div>
        <div className={styles.controls}>
          <label className={styles.sortWrap}>
            <span className={styles.sortLabel}>Sort</span>
            <select
              className={styles.sortSelect}
              value={sort}
              onChange={(e) => setSort(e.target.value)}
            >
              <option value="newest">Newest first</option>
              <option value="oldest">Oldest first</option>
              <option value="rating_desc">Highest rating</option>
              <option value="rating_asc">Lowest rating</option>
            </select>
          </label>
          {!showForm && (
            <button className={styles.writeBtn} onClick={() => setShowForm(true)}>
              Write a review
            </button>
          )}
        </div>
      </div>

      {showForm && (
        <div className={styles.formSection}>
          <div className={styles.formHeader}>
            <h3 className={styles.formTitle}>Your review</h3>
            <button className={styles.cancelBtn} onClick={() => setShowForm(false)}>Cancel</button>
          </div>
          <ReviewForm productId={productId} onReviewAdded={handleReviewAdded} />
        </div>
      )}

      {loading ? (
        <div className={styles.skeleton}>
          {[1, 2, 3].map((i) => <div key={i} className={styles.skeletonCard} />)}
        </div>
      ) : reviews.length === 0 && !showForm ? (
        <div className={styles.empty}>
          <p>No reviews yet. Be the first to review this product!</p>
          <button className={styles.writeBtn} onClick={() => setShowForm(true)}>
            Write a review
          </button>
        </div>
      ) : (
        <div className={styles.list}>
          {reviews.map((review) => (
            <ReviewCard key={review.id} review={review} />
          ))}
        </div>
      )}

      {!loading && reviews.length > 0 && hasMore && !showForm && (
        <div className={styles.loadMoreWrap}>
          <button
            className={styles.loadMoreBtn}
            onClick={handleLoadMore}
            disabled={loadingMore}
          >
            {loadingMore ? 'Loading…' : 'Load more reviews'}
          </button>
        </div>
      )}
    </section>
  )
}
