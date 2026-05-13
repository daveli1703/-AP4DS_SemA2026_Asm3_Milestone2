import styles from './WishlistButton.module.css'

export default function WishlistButton({ saved, onToggle }) {
  function handleClick(e) {
    e.preventDefault()
    e.stopPropagation()
    onToggle()
  }

  return (
    <button
      className={`${styles.btn} ${saved ? styles.saved : ''}`}
      onClick={handleClick}
      aria-label={saved ? 'Remove from wishlist' : 'Save to wishlist'}
      title={saved ? 'Remove from wishlist' : 'Save to wishlist'}
    >
      <svg viewBox="0 0 24 24" strokeWidth="1.8">
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
      </svg>
    </button>
  )
}
