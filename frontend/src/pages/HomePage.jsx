import React, { useState, useEffect } from 'react';
import { useLocation,Link } from 'react-router-dom';
import '../App.css';
import './HomePage.css';

function HomePage() {
  const [allProducts, setAllProducts] = useState([]); // Master list
  const [displayProducts, setDisplayProducts] = useState([]); // Filtered list
  const [brands, setBrands] = useState([]); // Unique brands for dropdown
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedBrand, setSelectedBrand] = useState('All Brands');
  const location = useLocation();
  useEffect(() => {
    fetch('/api/products')
      .then(res => res.json())
      .then(data => {
        setAllProducts(data);
        setDisplayProducts(data.slice(0, 8));
        
        // Task 4: Extract unique brands from the 'brand' column
        const uniqueBrands = ['All Brands', ...new Set(data.map(p => p.brand).filter(Boolean))];
        setBrands(uniqueBrands.sort());
      })
      .catch(err => console.error("Error:", err));
  }, []);

  useEffect(() => {
    fetch('/api/products')
      .then(res => res.json())
      .then(data => {
        setAllProducts(data);
        
        // CHECK THE URL: Did the user click a brand link in the breadcrumb?
        const params = new URLSearchParams(location.search);
        const brandFromUrl = params.get('brand');

        if (brandFromUrl) {
          // If a brand is in the URL, filter by it immediately
          setSelectedBrand(brandFromUrl);
          const filtered = data.filter(p => p.brand === brandFromUrl);
          setDisplayProducts(filtered);
        } else {
          // Normal load
          setDisplayProducts(data.slice(0, 8));
        }
      });
  }, [location.search]); // Re-run if the URL parameters change
  // Combined Filter Logic: Search + Brand
  useEffect(() => {
    let filtered = allProducts;

    // 1. Filter by Brand
    if (selectedBrand !== 'All Brands') {
      filtered = filtered.filter(p => p.brand === selectedBrand);
    }

    // 2. Filter by Search Term (Name, Brand, or Description)
    if (searchTerm.trim() !== '') {
      filtered = filtered.filter(p => 
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.brand?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // If no filters are active, show the featured 8. Otherwise, show results.
    if (searchTerm === '' && selectedBrand === 'All Brands') {
      setDisplayProducts(allProducts.slice(0, 8));
    } else {
      setDisplayProducts(filtered);
    }
  }, [searchTerm, selectedBrand, allProducts]);

  return (
    <div className="all-products-page">
      <div className="search-banner">
        <h2 className="section-title">All Products</h2>
        <div className="filter-controls">
          {/* Task 1: Search Input */}
          <input 
            type="text" 
            placeholder="Search products..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="main-search-bar"
          />

          {/* Task 4: Brand Dropdown */}
          <select 
            className="brand-select"
            value={selectedBrand}
            onChange={(e) => setSelectedBrand(e.target.value)}
          >
            {brands.map(brand => (
              <option key={brand} value={brand}>{brand}</option>
            ))}
          </select>
        </div>
        {(searchTerm || selectedBrand !== 'All Brands') && (
          <p className="search-count">{displayProducts.length} items found</p>
        )}
      </div>
      
      <div className="main-layout">
        <main className="product-grid-container">
          <div className="grid">
            {displayProducts.map(product => (
              <div key={product.id} className="luxury-card">
                <div className="card-badges">
                  <span className="badge featured">FEATURED</span>
                  <span className="badge bestseller">BESTSELLER</span>
                </div>
                <div className="visual-area">
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
                <div className="card-content">
                  <h4 className="product-full-name">{product.brand} {product.name}</h4>
                  <div className="price-row">
                    <span className="current-price">${product.price}</span>
                  </div>
                  <div className="rating-row">
                    <span className="stars">{product.rating} ★</span>
                    <span className="count">({product.ratingCount})</span>
                  </div>
                  <Link to={`/product/${product.id}`} className="view-btn">View Details</Link>
                </div>
              </div>
            ))}
          </div>
        </main>
      </div>
    </div>
  );
}

export default HomePage;