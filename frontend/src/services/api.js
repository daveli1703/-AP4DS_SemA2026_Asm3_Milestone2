const BASE = '/api'

async function request(path, options) {
  const res = await fetch(`${BASE}${path}`, options)
  if (!res.ok) {
    const err = new Error(`API error ${res.status}`)
    err.status = res.status
    throw err
  }
  return res.json()
}

export const api = {
  getProducts(skip = 0, limit = 20) {
    return request(`/products?skip=${skip}&limit=${limit}`)
  },

  searchProducts(query) {
    return request(`/products/search?q=${encodeURIComponent(query)}`)
  },

  getProduct(id) {
    return request(`/products/${id}`)
  },

  getReviews(id) {
    return request(`/products/${id}/reviews`)
  },

  getRecommendations(id, topK = 5) {
    return request(`/products/${id}/recommendations?top_k=${topK}`)
  },

  getSentimentSummary(id) {
    return request(`/products/${id}/sentiment-summary`)
  },

  submitReview(productId, body) {
    return request(`/products/${productId}/reviews`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
  },

  getReview(reviewId) {
    return request(`/reviews/${reviewId}`)
  },

  overrideLabel(reviewId, recommended) {
    return request(`/reviews/${reviewId}/label`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ recommended }),
    })
  },
}
