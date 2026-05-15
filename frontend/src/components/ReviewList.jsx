import { useState, useEffect } from 'react'
import ReviewCard from './ReviewCard'
import ReviewForm from './ReviewForm'
import { api } from '../services/api'
import styles from './ReviewList.module.css'

export default function ReviewList({ productId }) {
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)

  useEffect(() => {
    api.getReviews(productId)
      .then(setReviews)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [productId])

  function handleReviewAdded(newReview) {
    setReviews((prev) => [newReview, ...prev])
    setShowForm(false)
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
        {!showForm && (
          <button className={styles.writeBtn} onClick={() => setShowForm(true)}>
            Write a review
          </button>
        )}
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
    </section>
  )
}
