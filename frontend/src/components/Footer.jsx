import React from 'react';
import './Footer.css';

const Footer = ({ onLegalClick }) => {
  return (
    <footer className="app-footer">
      <div className="footer-content">
        <div className="footer-links">
          <button 
            className="footer-link"
            onClick={() => onLegalClick('mentions')}
          >
            Mentions légales
          </button>
          <span className="separator">•</span>
          <button 
            className="footer-link"
            onClick={() => onLegalClick('privacy')}
          >
            Confidentialité
          </button>
          <span className="separator">•</span>
          <button 
            className="footer-link"
            onClick={() => onLegalClick('cookies')}
          >
            Cookies
          </button>
          <span className="separator">•</span>
          <button 
            className="footer-link"
            onClick={() => onLegalClick('terms')}
          >
            CGU
          </button>
          <span className="separator">•</span>
          <button 
            className="footer-link"
            onClick={() => onLegalClick('contact')}
          >
            Contact
          </button>
        </div>
        
        <div className="footer-info">
          <p>© {new Date().getFullYear()} FRIDAY</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
