import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import ReviewCard from '../components/ReviewCard'
import { api } from '../services/api'
import styles from './ReviewPage.module.css'

export default function ReviewPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [review, setReview] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.getReview(id)
      .then(setReview)
      .catch((err) => {
        setError(err.status === 404 ? 'Review not found.' : 'Failed to load review.')
      })
      .finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return (
      <div className={styles.page}>
        <div className={styles.container}>
          <div className={styles.skeletonTitle} />
          <div className={styles.skeletonBody} />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={styles.page}>
        <div className={styles.container}>
          <p className={styles.errorText}>{error}</p>
          <button className={styles.backBtn} onClick={() => navigate(-1)}>Go back</button>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <nav className={styles.breadcrumb}>
          <Link to="/" className={styles.bcLink}>Products</Link>
          <span className={styles.bcSep}>/</span>
          <Link to={`/products/${review.product_id}`} className={styles.bcLink}>
            Product #{review.product_id}
          </Link>
          <span className={styles.bcSep}>/</span>
          <span className={styles.bcCurrent}>Review #{review.id}</span>
        </nav>

        <h1 className={styles.heading}>Review</h1>
        <p className={styles.sub}>
          Permanent link — this review will always be accessible here.
        </p>

        <div className={styles.card}>
          <ReviewCard review={review} showModelDetail={true} />
        </div>

        <Link to={`/products/${review.product_id}`} className={styles.productLink}>
          View product page
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
            <line x1="5" y1="12" x2="19" y2="12" />
            <polyline points="12 5 19 12 12 19" />
          </svg>
        </Link>
      </div>
    </div>
  )
}
