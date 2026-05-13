import { useState, useCallback } from 'react'

const KEY = 'glow_wishlist'

function load() {
  try {
    return JSON.parse(localStorage.getItem(KEY)) ?? []
  } catch {
    return []
  }
}

function save(items) {
  localStorage.setItem(KEY, JSON.stringify(items))
}

export function useWishlist() {
  const [items, setItems] = useState(load)

  const toggle = useCallback((product) => {
    setItems((prev) => {
      const exists = prev.some((p) => p.id === product.id)
      const next = exists
        ? prev.filter((p) => p.id !== product.id)
        : [...prev, { id: product.id, name: product.name, brand: product.brand, price: product.price, image_url: product.image_url }]
      save(next)
      return next
    })
  }, [])

  const isSaved = useCallback((id) => items.some((p) => p.id === id), [items])

  return { items, toggle, isSaved }
}
