import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import '../App.css';
import { Link } from 'react-router-dom';
import './ProductPage.css';
import { useNavigate } from 'react-router-dom';
function ProductPage() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [similarItems, setSimilarItems] = useState([]);
  const navigate = useNavigate();
  const [reviewText, setReviewText] = useState('');
  const [predictedLabel, setPredictedLabel] = useState(null); 
  const [userOverride, setUserOverride] = useState(''); 

  useEffect(() => {
    window.scrollTo(0, 0);
    // Fetch Product Details
    setReviewText('');           // Clears the text area
    setPredictedLabel(null);     // Hides the AI prediction box
    setUserOverride('');         // Resets the user's manual choice
    fetch(`/api/products/${id}`)
      .then(res => res.json())
      .then(data => setProduct(data));

    // Fetch Recommendations (Task 3)
    fetch(`/api/products/${id}/recommendations`)
      .then(res => res.json())
      .then(data => setSimilarItems(data));
  }, [id]);

// 1. Consolidated Prediction Logic
const handleReviewBlur = async (e) => {
  const currentText = e.target.value.trim();
  
  // If user clears the text, reset the AI UI
  if (currentText.length <= 10) {
    setPredictedLabel(null);
    return;
  }

  try {
    const response = await fetch('/api/predict-review', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        review: currentText,
        productId: id // Required for Fusion Logic (Rating + Price)
      })
    });
    
    const data = await response.json();
    setPredictedLabel(data.label); 
    setUserOverride(data.label); 
  } catch (error) {
    console.error("AI Analysis failed:", error);
  }
};

// 2. Robust Submission Logic
const submitReview = async (e) => {
  e.preventDefault();
  
  // Ensure we don't submit if userOverride wasn't set yet
  const finalLabel = userOverride || predictedLabel || 'Buy';

  const reviewData = { 
    text: reviewText, 
    finalLabel: finalLabel, 
    productId: id,
    timestamp: new Date().toISOString() // Good for sorting later
  };

  try {
    const response = await fetch(`/api/products/${id}/reviews`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reviewData)
    });

    if (response.ok) {
      alert("Review saved successfully!");
      setReviewText('');
      setPredictedLabel(null);
      setUserOverride('');

    }
  } catch (error) {
    alert("Could not save review. Please try again.");
  }
};

  if (!product) return <div className="loading">Loading Product Details...</div>;

  return (
    <div className="product-page">
      {/* Breadcrumb Navigation */}
      <nav className="breadcrumb-nav">
  <Link to="/" className="breadcrumb-home">Home</Link>
  <span className="separator">/</span>
  
  {/* Now clickable: Sends the brand name as a URL parameter */}
  <Link 
    to={`/?brand=${encodeURIComponent(product.brand)}`} 
    className="breadcrumb-brand-link"
  >
    {product.brand}
  </Link>
  
  <span className="separator">/</span>
  <span className="breadcrumb-current">{product.name}</span>
</nav>

      {/* Main Product Layout: Two Columns */}
      <div className="product-main-container">
        
        {/* Left Column: Premium Visual Placeholder */}
        <div className="product-visual-section">
           <button className="back-floating-btn" onClick={() => navigate(-1)}>←</button>
           <div className="main-visual-box">
              {product.imageUrl ? (
      <img 
        src={product.imageUrl} 
        alt={product.brand} 
        className="brand-logo-fit" 
      />
    ) : (
      <div className="fallback-avatar">
        {product.brand ? product.brand.charAt(0) : 'P'}
      </div>
    )}
           </div>
        </div>

        {/* Right Column: Information Section */}
        <div className="product-details-section">
          <h1 className="product-full-title">{product.name}</h1>
          
          <div className="rating-metrics">
            <span className="stars">{product.rating} ★</span>
            <span className="rating-count">{product.ratingCount} ratings</span>
            <span className="review-divider"> & </span>
            <span className="review-count">{product.description.length} reviews</span>
          </div>

          <div className="price-container">
            <span className="discounted-price">${product.price}</span>
          </div>

          <p className="product-tagline">Your Daily Beauty Essential</p>
          {product.url && (
    <div className="external-link-container">
      <a 
        href={product.url} 
        target="_blank" 
        rel="noopener noreferrer" 
        className="visit-site-btn"
      >
        View on Official Website
      </a>
    </div>
  )}
        </div>
      </div>

      {/* Task 2: AI Sentiment Analysis Section */}
      <form className="review-form" onSubmit={submitReview}>
  <h3>Leave a Review</h3>
  <textarea
    value={reviewText}
    onChange={(e) => setReviewText(e.target.value)}
    onBlur={handleReviewBlur} // The AI magic happens here
    placeholder="What did you think of this product?"
    required
  />

  {predictedLabel && (
    <div className="ai-feedback-area">
      <p>🤖 AI thinks you would: <strong>{predictedLabel}</strong></p>
      
      <div className="user-choice">
        <label>Correct the AI if needed: </label>
        <select 
          value={userOverride} 
          onChange={(e) => setUserOverride(e.target.value)}
        >
          <option value="Buy">Buy</option>
          <option value="Not Buy">Not Buy</option>
        </select>
      </div>
    </div>
  )}

  <button type="submit" className="submit-btn" disabled={!reviewText}>
    Submit Review
  </button>
  </form>

      {/* Task 3: Recommendations */}
     <div className="recommendations-section">
  <div className="section-header">
    <h3>Similar Products</h3>
    <p>Based on product descriptions and ingredients analysis</p>
  </div>
  <div className="similar-items-grid">
    {similarItems.map(item => (
      <Link to={`/product/${item.id}`} key={item.id} className="similar-card-link">
        <div className="similar-card">
          {/* FIX: Use item.imageUrl and item.brand instead of product */}
          <div className="small-placeholder">
            {item.imageUrl ? (
              <img 
                src={item.imageUrl} 
                alt={item.brand} 
                className="brand-logo-fit" 
              />
            ) : (
              <div className="fallback-avatar">
                {/* FIX: Use item.brand for the initial */}
                {item.brand ? item.brand.charAt(0) : 'P'}
              </div>
            )}
          </div>
          <h4>{item.name}</h4>
          <div className="match-badge">
            <span className="score-text">{item.similarityScore}% Match</span>
          </div>
        </div>
      </Link>
    ))}
  </div>
  <div className="customer-reviews-list">
  <h3>Community Reviews</h3>
  {product.reviews && product.reviews.length > 0 ? (
    product.reviews.map((rev, index) => (
      <div key={index} className="review-item">
        <p>"{rev.text}"</p>
        <span className={`intent-badge ${rev.finalLabel}`}>
          Intent: {rev.finalLabel}
        </span>
      </div>
    ))
  ) : (
    <p>No reviews yet. Be the first to write one!</p>
  )}
</div>
</div>
    </div>

  );
}

export default ProductPage;