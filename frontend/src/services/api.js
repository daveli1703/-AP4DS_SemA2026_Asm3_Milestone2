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

function buildQuery(params) {
  const qs = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return
    qs.append(key, value)
  })
  const out = qs.toString()
  return out ? `?${out}` : ''
}

export const api = {
  getProducts(skip = 0, limit = 20, filters = {}) {
    return request(`/products${buildQuery({ skip, limit, ...filters })}`)
  },

  searchProducts(query, filters = {}) {
    return request(`/products/search${buildQuery({ q: query, ...filters })}`)
  },

  getProductFilters() {
    return request('/products/filters')
  },

  getProduct(id) {
    return request(`/products/${id}`)
  },

  getReviews(id, options = {}) {
    return request(`/products/${id}/reviews${buildQuery(options)}`)
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
