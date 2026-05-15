import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { api } from '../services/api'
import ReviewList from '../components/ReviewList'
import RecommendationSection from '../components/RecommendationSection'
import styles from './ProductDetailPage.module.css'

const PLACEHOLDER = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600"%3E%3Crect width="600" height="600" fill="%23f2ece4"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="18" fill="%239e9793"%3ENo image available%3C/text%3E%3C/svg%3E'

function StarRating({ rating }) {
  const full = Math.floor(rating)
  const half = rating % 1 >= 0.5
  const empty = 5 - full - (half ? 1 : 0)
  return (
    <span className={styles.stars} aria-label={`${rating} out of 5 stars`}>
      {'★'.repeat(full)}
      {half ? '½' : ''}
      {'☆'.repeat(empty)}
      <span className={styles.ratingNum}>{rating.toFixed(1)}</span>
    </span>
  )
}

function formatPrice(price) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(price)
}

export default function ProductDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [product, setProduct] = useState(null)
  const [sentiment, setSentiment] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [recRefresh, setRecRefresh] = useState(0)

  useEffect(() => {
    setLoading(true)
    setError(null)
    setProduct(null)
    setSentiment(null)

    Promise.all([
      api.getProduct(id),
      api.getSentimentSummary(id).catch(() => null),
    ])
      .then(([prod, sent]) => {
        setProduct(prod)
        setSentiment(sent)
      })
      .catch((err) => {
        setError(err.status === 404 ? 'Product not found.' : 'Failed to load product. Make sure the backend is running.')
      })
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <LoadingState />
  if (error) return <ErrorState message={error} onBack={() => navigate(-1)} />

  const { name, brand, category, description, price, image_url } = product

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <nav className={styles.breadcrumb}>
          <Link to="/" className={styles.breadcrumbLink}>Products</Link>
          <span className={styles.breadcrumbSep}>/</span>
          {brand && (
            <>
              <span className={styles.breadcrumbLink}>{brand}</span>
              <span className={styles.breadcrumbSep}>/</span>
            </>
          )}
          <span className={styles.breadcrumbCurrent}>{name}</span>
        </nav>

        <div className={styles.layout}>
          <div className={styles.imageCol}>
            <div className={styles.imageWrap}>
              <img
                src={image_url || PLACEHOLDER}
                alt={name}
                className={styles.image}
                onError={(e) => { e.currentTarget.src = PLACEHOLDER }}
              />
            </div>
          </div>

          <div className={styles.infoCol}>
            {brand && <p className={styles.brand}>{brand}</p>}
            <h1 className={styles.name}>{name}</h1>

            {category && category !== 'General' && (
              <span className={styles.categoryTag}>{category}</span>
            )}

            <p className={styles.price}>{formatPrice(price)}</p>

            {sentiment && sentiment.review_count > 0 && (
              <div className={styles.ratingRow}>
                <StarRating rating={sentiment.avg_rating} />
                <span className={styles.reviewCount}>
                  {sentiment.review_count} review{sentiment.review_count !== 1 ? 's' : ''}
                </span>
              </div>
            )}

            {description && description !== name && (
              <div className={styles.descriptionSection}>
                <h2 className={styles.descLabel}>About this product</h2>
                <p className={styles.description}>{description}</p>
              </div>
            )}

            {sentiment && sentiment.review_count > 0 && (
              <SentimentPanel sentiment={sentiment} />
            )}
          </div>
        </div>

        <RecommendationSection productId={id} refreshKey={recRefresh} />
        <ReviewList
          productId={id}
          onReviewAdded={() => setRecRefresh((prev) => prev + 1)}
        />
      </div>
    </div>
  )
}

function SentimentPanel({ sentiment }) {
  const { buy_rate, sentiment_breakdown, top_positive_keywords, top_negative_keywords } = sentiment
  const { positive_pct, negative_pct, neutral_pct } = sentiment_breakdown

  return (
    <div className={styles.sentimentPanel}>
      <h2 className={styles.sentimentTitle}>Review Sentiment</h2>

      <div className={styles.buyRate}>
        <span className={styles.buyRateNum}>{Math.round(buy_rate * 100)}%</span>
        <span className={styles.buyRateLabel}>of reviewers recommend this product</span>
      </div>

      <div className={styles.sentimentBars}>
        <SentimentBar label="Positive" pct={positive_pct} color="#7bba8e" />
        <SentimentBar label="Neutral" pct={neutral_pct} color="#c4b99a" />
        <SentimentBar label="Negative" pct={negative_pct} color="#d48b8b" />
      </div>

      {top_positive_keywords?.length > 0 && (
        <div className={styles.keywords}>
          <p className={styles.keywordsLabel}>Top positive themes</p>
          <div className={styles.keywordTags}>
            {top_positive_keywords.slice(0, 6).map((kw) => (
              <span key={kw} className={`${styles.tag} ${styles.tagPositive}`}>{kw}</span>
            ))}
          </div>
        </div>
      )}

      {top_negative_keywords?.length > 0 && (
        <div className={styles.keywords}>
          <p className={styles.keywordsLabel}>Top negative themes</p>
          <div className={styles.keywordTags}>
            {top_negative_keywords.slice(0, 6).map((kw) => (
              <span key={kw} className={`${styles.tag} ${styles.tagNegative}`}>{kw}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function SentimentBar({ label, pct, color }) {
  return (
    <div className={styles.barRow}>
      <span className={styles.barLabel}>{label}</span>
      <div className={styles.barTrack}>
        <div className={styles.barFill} style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className={styles.barPct}>{pct.toFixed(0)}%</span>
    </div>
  )
}

function LoadingState() {
  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <div className={styles.loadingLayout}>
          <div className={`${styles.skeleton} ${styles.skeletonImage}`} />
          <div className={styles.skeletonInfo}>
            <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: '40%', height: 14 }} />
            <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: '80%', height: 28, marginTop: 12 }} />
            <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: '30%', height: 24, marginTop: 16 }} />
          </div>
        </div>
      </div>
    </div>
  )
}

function ErrorState({ message, onBack }) {
  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <div className={styles.errorBox}>
          <p className={styles.errorText}>{message}</p>
          <button className={styles.backBtn} onClick={onBack}>Go back</button>
        </div>
      </div>
    </div>
  )
}
