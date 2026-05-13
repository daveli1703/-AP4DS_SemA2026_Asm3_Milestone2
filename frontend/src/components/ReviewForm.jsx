import { useState } from 'react'
import StarInput from './StarInput'
import { api } from '../services/api'
import styles from './ReviewForm.module.css'

const MODEL_LABELS = {
  naive_bayes_text: 'Naive Bayes (text)',
  naive_bayes_text_title: 'Naive Bayes (text + title)',
  logistic_extra_info: 'Logistic Regression',
}

export default function ReviewForm({ productId, onReviewAdded }) {
  const [stage, setStage] = useState('form')
  const [fields, setFields] = useState({
    reviewer_name: '',
    rating: 0,
    review_title: '',
    review_text: '',
  })
  const [errors, setErrors] = useState({})
  const [submittedReview, setSubmittedReview] = useState(null)
  const [apiError, setApiError] = useState(null)

  function set(key, value) {
    setFields((f) => ({ ...f, [key]: value }))
    setErrors((e) => ({ ...e, [key]: null }))
  }

  function validate() {
    const errs = {}
    if (!fields.reviewer_name.trim()) errs.reviewer_name = 'Name is required.'
    if (fields.rating === 0) errs.rating = 'Please select a rating.'
    if (!fields.review_text.trim()) errs.review_text = 'Review text is required.'
    return errs
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length) { setErrors(errs); return }

    setStage('submitting')
    setApiError(null)
    try {
      const review = await api.submitReview(productId, {
        reviewer_name: fields.reviewer_name.trim(),
        rating: fields.rating,
        review_title: fields.review_title.trim() || undefined,
        review_text: fields.review_text.trim(),
        recommended: null,
      })
      setSubmittedReview(review)
      setStage('prediction')
    } catch (err) {
      setApiError('Failed to submit review. Please try again.')
      setStage('form')
    }
  }

  async function handleConfirm() {
    setStage('done')
    onReviewAdded(submittedReview)
  }

  async function handleOverride() {
    setStage('overriding')
    try {
      const updated = await api.overrideLabel(
        submittedReview.id,
        !submittedReview.predicted_recommended
      )
      setStage('done')
      onReviewAdded(updated)
    } catch {
      setApiError('Override failed. Please try again.')
      setStage('prediction')
    }
  }

  function reset() {
    setStage('form')
    setFields({ reviewer_name: '', rating: 0, review_title: '', review_text: '' })
    setErrors({})
    setSubmittedReview(null)
    setApiError(null)
  }

  if (stage === 'done') {
    return (
      <div className={styles.done}>
        <div className={styles.doneIcon}>✓</div>
        <h3 className={styles.doneTitle}>Review submitted!</h3>
        <p className={styles.doneSub}>Your review is now visible on this product.</p>
        <button className={styles.ghostBtn} onClick={reset}>Write another review</button>
      </div>
    )
  }

  if (stage === 'prediction' || stage === 'overriding') {
    return <PredictionResult
      review={submittedReview}
      onConfirm={handleConfirm}
      onOverride={handleOverride}
      loading={stage === 'overriding'}
      apiError={apiError}
    />
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit} noValidate>
      <div className={styles.row}>
        <label className={styles.label}>
          Your name <span className={styles.req}>*</span>
          <input
            className={`${styles.input} ${errors.reviewer_name ? styles.inputError : ''}`}
            type="text"
            value={fields.reviewer_name}
            onChange={(e) => set('reviewer_name', e.target.value)}
            placeholder="Jane Doe"
            disabled={stage === 'submitting'}
          />
          {errors.reviewer_name && <span className={styles.fieldError}>{errors.reviewer_name}</span>}
        </label>

        <label className={styles.label}>
          Rating <span className={styles.req}>*</span>
          <div className={styles.starWrap}>
            <StarInput value={fields.rating} onChange={(v) => set('rating', v)} />
          </div>
          {errors.rating && <span className={styles.fieldError}>{errors.rating}</span>}
        </label>
      </div>

      <label className={styles.label}>
        Review title <span className={styles.optional}>(optional)</span>
        <input
          className={styles.input}
          type="text"
          value={fields.review_title}
          onChange={(e) => set('review_title', e.target.value)}
          placeholder="Summarise your experience…"
          disabled={stage === 'submitting'}
        />
      </label>

      <label className={styles.label}>
        Review <span className={styles.req}>*</span>
        <textarea
          className={`${styles.textarea} ${errors.review_text ? styles.inputError : ''}`}
          value={fields.review_text}
          onChange={(e) => set('review_text', e.target.value)}
          placeholder="Tell others about your experience with this product…"
          rows={4}
          disabled={stage === 'submitting'}
        />
        {errors.review_text && <span className={styles.fieldError}>{errors.review_text}</span>}
      </label>

      {apiError && <p className={styles.apiError}>{apiError}</p>}

      <button
        className={styles.submitBtn}
        type="submit"
        disabled={stage === 'submitting'}
      >
        {stage === 'submitting' ? 'Submitting…' : 'Submit review'}
      </button>
    </form>
  )
}

function PredictionResult({ review, onConfirm, onOverride, loading, apiError }) {
  const { predicted_recommended, ensemble_score, model_scores } = review
  const buys = predicted_recommended === true
  const confidence = ensemble_score != null ? Math.round(ensemble_score * 100) : null
  const uncertain = confidence != null && confidence >= 40 && confidence <= 60

  return (
    <div className={styles.prediction}>
      <div className={styles.predHeader}>
        <h3 className={styles.predTitle}>ML Prediction</h3>
        <p className={styles.predSub}>Based on your review text, our models predict:</p>
      </div>

      <div className={`${styles.verdict} ${buys ? styles.verdictYes : styles.verdictNo}`}>
        <span className={styles.verdictIcon}>{buys ? '✓' : '✗'}</span>
        <div>
          <p className={styles.verdictText}>
            {buys ? 'You would buy this again' : 'You would not buy this again'}
          </p>
          {uncertain && (
            <p className={styles.verdictUncertain}>Low confidence — models are unsure</p>
          )}
        </div>
      </div>

      {confidence != null && (
        <div className={styles.confRow}>
          <span className={styles.confLabel}>Confidence</span>
          <div className={styles.confBar}>
            <div
              className={`${styles.confFill} ${buys ? styles.confFillYes : styles.confFillNo}`}
              style={{ width: `${confidence}%` }}
            />
          </div>
          <span className={styles.confNum}>{confidence}%</span>
        </div>
      )}

      {model_scores && (
        <div className={styles.breakdown}>
          <p className={styles.breakdownTitle}>Model breakdown</p>
          {Object.entries(model_scores).map(([key, score]) => {
            const pct = Math.round(score * 100)
            return (
              <div key={key} className={styles.modelRow}>
                <span className={styles.modelName}>{MODEL_LABELS[key] ?? key}</span>
                <div className={styles.modelBar}>
                  <div
                    className={`${styles.modelFill} ${score >= 0.5 ? styles.mfYes : styles.mfNo}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <span className={styles.modelPct}>{pct}%</span>
              </div>
            )
          })}
        </div>
      )}

      {apiError && <p className={styles.apiError}>{apiError}</p>}

      <div className={styles.predActions}>
        <p className={styles.predPrompt}>Does this match your opinion?</p>
        <div className={styles.predBtns}>
          <button
            className={styles.confirmBtn}
            onClick={onConfirm}
            disabled={loading}
          >
            Confirm — yes, that's right
          </button>
          <button
            className={styles.overrideBtn}
            onClick={onOverride}
            disabled={loading}
          >
            {loading ? 'Saving…' : `Override — I would ${buys ? 'not ' : ''}buy this`}
          </button>
        </div>
      </div>
    </div>
  )
}
