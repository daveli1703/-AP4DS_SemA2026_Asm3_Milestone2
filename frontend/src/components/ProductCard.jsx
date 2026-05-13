import { Link } from 'react-router-dom'
import WishlistButton from './WishlistButton'
import styles from './ProductCard.module.css'

const PLACEHOLDER = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400"%3E%3Crect width="400" height="400" fill="%23f2ece4"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="14" fill="%239e9793"%3ENo image%3C/text%3E%3C/svg%3E'

function formatPrice(price) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(price)
}

export default function ProductCard({ product, saved, onToggleWishlist }) {
  const { id, name, brand, category, price, image_url } = product

  return (
    <Link to={`/products/${id}`} className={styles.card}>
      <div className={styles.imageWrap}>
        <img
          src={image_url || PLACEHOLDER}
          alt={name}
          className={styles.image}
          loading="lazy"
          onError={(e) => { e.currentTarget.src = PLACEHOLDER }}
        />
        {category && category !== 'General' && (
          <span className={styles.categoryBadge}>{category}</span>
        )}
        {onToggleWishlist && (
          <div className={styles.wishlistBtn}>
            <WishlistButton saved={saved} onToggle={() => onToggleWishlist(product)} />
          </div>
        )}
      </div>
      <div className={styles.info}>
        {brand && <p className={styles.brand}>{brand}</p>}
        <h3 className={styles.name}>{name}</h3>
        <p className={styles.price}>{formatPrice(price)}</p>
      </div>
    </Link>
  )
}
