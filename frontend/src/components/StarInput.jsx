import { useState } from 'react'
import styles from './StarInput.module.css'

export default function StarInput({ value, onChange }) {
  const [hovered, setHovered] = useState(0)

  return (
    <div className={styles.wrap} role="radiogroup" aria-label="Rating">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          className={`${styles.star} ${star <= (hovered || value) ? styles.active : ''}`}
          onClick={() => onChange(star)}
          onMouseEnter={() => setHovered(star)}
          onMouseLeave={() => setHovered(0)}
          aria-label={`${star} star${star !== 1 ? 's' : ''}`}
          aria-pressed={value === star}
        >
          ★
        </button>
      ))}
      {value > 0 && (
        <span className={styles.label}>{value}.0 / 5.0</span>
      )}
    </div>
  )
}
