import { Link } from 'react-router-dom'
import WishlistButton from './WishlistButton'
import styles from './ProductCard.module.css'

const getCosmeticImage = (id) => `https://loremflickr.com/400/400/cosmetics,makeup,beauty?lock=${id}`

function formatPrice(price) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(price)
}

export default function ProductCard({ product, saved, onToggleWishlist }) {
  const { id, name, brand, category, price, image_url } = product

  return (
    <Link to={`/products/${id}`} className={styles.card}>
      <div className={styles.imageWrap}>
        <img
          src={getCosmeticImage(id)}
          alt={name}
          className={styles.image}
          loading="lazy"
          onError={(e) => { e.currentTarget.src = getCosmeticImage(id + 100) }}
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
