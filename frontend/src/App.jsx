import { Routes, Route, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import Header from './components/Header'
import HomePage from './pages/HomePage'
import ProductDetailPage from './pages/ProductDetailPage'
import ReviewPage from './pages/ReviewPage'

function ScrollToTop() {
  const { pathname } = useLocation()
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [pathname])
  return null
}

export default function App() {
  return (
    <>
      <ScrollToTop />
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/products/:id" element={<ProductDetailPage />} />
          <Route path="/reviews/:id" element={<ReviewPage />} />
        </Routes>
      </main>
    </>
  )
}
