import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import styles from './RecommendationSection.module.css'

const getCosmeticImage = (id) => `https://loremflickr.com/200/200/cosmetics,makeup,beauty?lock=${id}`

function formatPrice(price) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(price)
}

export default function RecommendationSection({ productId }) {
  const [recs, setRecs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    api.getRecommendations(productId, 8)
      .then((data) => setRecs(data.results ?? []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [productId])

  if (!loading && recs.length === 0) return null

  return (
    <section className={styles.section}>
      <h2 className={styles.title}>You might also like</h2>

      <div className={styles.track}>
        {loading
          ? Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className={styles.skeleton} />
            ))
          : recs.map((item) => (
              <Link key={item.id} to={`/products/${item.id}`} className={styles.card}>
                <div className={styles.imageWrap}>
                  <img
                    src={getCosmeticImage(item.id)}
                    alt={item.name}
                    className={styles.image}
                    loading="lazy"
                    onError={(e) => { e.currentTarget.src = getCosmeticImage(item.id + 100) }}
                  />
                  <span className={styles.similarity}>
                    {Math.round(item.similarity_score * 100)}% match
                  </span>
                </div>
                <div className={styles.info}>
                  {item.brand && <p className={styles.brand}>{item.brand}</p>}
                  <p className={styles.name}>{item.name}</p>
                  <p className={styles.price}>{formatPrice(item.price)}</p>
                </div>
              </Link>
            ))}
      </div>
    </section>
  )
}
