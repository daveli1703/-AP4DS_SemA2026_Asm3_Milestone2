import { Link } from 'react-router-dom'
import styles from './ReviewCard.module.css'

function Stars({ rating }) {
  const full = Math.floor(rating)
  const empty = 5 - full
  return (
    <span className={styles.stars} aria-label={`${rating} out of 5`}>
      {'★'.repeat(full)}{'☆'.repeat(empty)}
    </span>
  )
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-AU', { year: 'numeric', month: 'short', day: 'numeric' })
}

const MODEL_LABELS = {
  naive_bayes_text: 'Naive Bayes (text)',
  naive_bayes_text_title: 'Naive Bayes (text + title)',
  logistic_extra_info: 'Logistic Regression',
}

export default function ReviewCard({ review, showModelDetail = false }) {
  const {
    id,
    reviewer_name,
    rating,
    review_title,
    review_text,
    recommended,
    predicted_recommended,
    user_overridden,
    ensemble_score,
    model_scores,
    created_at,
  } = review

  const buys = recommended === true

  return (
    <article className={styles.card}>
      <div className={styles.header}>
        <div className={styles.meta}>
          <span className={styles.name}>{reviewer_name}</span>
          <span className={styles.dot}>·</span>
          <Stars rating={rating} />
          <span className={styles.dot}>·</span>
          <span className={styles.date}>{formatDate(created_at)}</span>
        </div>
        <Link to={`/reviews/${id}`} className={styles.permalink} title="Permanent link to this review">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
            <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
            <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
          </svg>
        </Link>
      </div>

      {review_title && <h4 className={styles.title}>{review_title}</h4>}
      <p className={styles.text}>{review_text}</p>

      <div className={styles.footer}>
        {recommended !== null && recommended !== undefined && (
          <span className={`${styles.badge} ${buys ? styles.badgeYes : styles.badgeNo}`}>
            {buys ? '✓ Recommends' : '✗ Does not recommend'}
            {user_overridden && <em className={styles.overrideNote}> (overridden)</em>}
          </span>
        )}

        {ensemble_score != null && (
          <span className={styles.confidence}>
            Confidence: {Math.round(ensemble_score * 100)}%
          </span>
        )}
      </div>

      {showModelDetail && model_scores && (
        <div className={styles.modelDetail}>
          <p className={styles.modelDetailTitle}>Model breakdown</p>
          {Object.entries(model_scores).map(([key, score]) => (
            <div key={key} className={styles.modelRow}>
              <span className={styles.modelName}>{MODEL_LABELS[key] ?? key}</span>
              <div className={styles.modelBar}>
                <div
                  className={`${styles.modelFill} ${score >= 0.5 ? styles.fillYes : styles.fillNo}`}
                  style={{ width: `${score * 100}%` }}
                />
              </div>
              <span className={styles.modelPct}>{Math.round(score * 100)}%</span>
            </div>
          ))}
          {predicted_recommended !== null && predicted_recommended !== undefined && (
            <p className={styles.predictedNote}>
              ML predicted: <strong>{predicted_recommended ? 'Recommend' : 'Not recommend'}</strong>
            </p>
          )}
        </div>
      )}
    </article>
  )
}
