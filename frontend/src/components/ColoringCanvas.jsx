import React, { useRef, useEffect, useState } from 'react';
import './ColoringCanvas.css';

const ColoringCanvas = ({ imageUrl, onClose, onSave }) => {
  const canvasRef = useRef(null);
  const [ctx, setCtx] = useState(null);
  const [selectedColor, setSelectedColor] = useState('#FF6B6B');
  const [tool, setTool] = useState('bucket'); // 'bucket' ou 'eraser'
  const [imageLoaded, setImageLoaded] = useState(false);
  const [originalImageData, setOriginalImageData] = useState(null);
  const [coloringData, setColoringData] = useState(null);
  
  // Palette de couleurs inspirée de Happy Color
  const colorPalette = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', 
    '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
    '#F8B739', '#52C41A', '#FF85C0', '#A8DADC',
    '#E07A5F', '#81C784', '#FFB6C1', '#20B2AA',
    '#DDA15E', '#BC6C25', '#FFDAB9', '#E6E6FA'
  ];

  // Initialiser le canvas et charger l'image
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const context = canvas.getContext('2d', { willReadFrequently: true });
    setCtx(context);

    // Charger l'image
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      // Ajuster la taille du canvas à l'image
      const maxWidth = window.innerWidth * 0.9;
      const maxHeight = window.innerHeight * 0.7;
      let width = img.width;
      let height = img.height;

      // Redimensionner si nécessaire
      if (width > maxWidth) {
        height = (maxWidth / width) * height;
        width = maxWidth;
      }
      if (height > maxHeight) {
        width = (maxHeight / height) * width;
        height = maxHeight;
      }

      canvas.width = width;
      canvas.height = height;

      // Dessiner l'image de fond
      context.drawImage(img, 0, 0, width, height);

      // Sauvegarder l'image originale pour la gomme
      setOriginalImageData(context.getImageData(0, 0, width, height));
      
      // Créer un calque de coloriage transparent
      const colorLayer = context.createImageData(width, height);
      setColoringData(colorLayer);
      
      setImageLoaded(true);
    };
    img.onerror = () => {
      console.error('Erreur de chargement de l\'image');
    };
    img.src = imageUrl;
  }, [imageUrl]);

  // Algorithme de flood fill (seau de peinture)
  const floodFill = (startX, startY, fillColor) => {
    if (!ctx || !originalImageData) return;

    const canvas = canvasRef.current;
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const pixels = imageData.data;
    const targetColor = getPixelColor(pixels, startX, startY, canvas.width);
    
    // Convertir la couleur de remplissage en RGB
    const fillRGB = hexToRgb(fillColor);
    
    // Ne rien faire si la couleur est déjà la bonne
    if (colorsMatch(targetColor, fillRGB)) return;

    const stack = [[startX, startY]];
    const visited = new Set();

    while (stack.length > 0) {
      const [x, y] = stack.pop();
      const key = `${x},${y}`;
      
      if (visited.has(key)) continue;
      if (x < 0 || x >= canvas.width || y < 0 || y >= canvas.height) continue;
      
      const currentColor = getPixelColor(pixels, x, y, canvas.width);
      
      // Vérifier si c'est une ligne noire (ne pas colorier les contours)
      if (isBlackLine(currentColor)) continue;
      
      if (!colorsMatch(currentColor, targetColor)) continue;
      
      visited.add(key);
      
      // Remplir le pixel
      setPixelColor(pixels, x, y, canvas.width, fillRGB);
      
      // Ajouter les pixels adjacents
      stack.push([x + 1, y]);
      stack.push([x - 1, y]);
      stack.push([x, y + 1]);
      stack.push([x, y - 1]);
    }

    ctx.putImageData(imageData, 0, 0);
  };

  // Fonction gomme : restaurer l'image originale
  const eraseArea = (startX, startY) => {
    if (!ctx || !originalImageData) return;

    const canvas = canvasRef.current;
    const currentData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const currentPixels = currentData.data;
    const originalPixels = originalImageData.data;
    
    const targetColor = getPixelColor(currentPixels, startX, startY, canvas.width);
    
    // Si c'est déjà blanc/transparent, ne rien faire
    if (isWhiteOrTransparent(targetColor)) return;

    const stack = [[startX, startY]];
    const visited = new Set();

    while (stack.length > 0) {
      const [x, y] = stack.pop();
      const key = `${x},${y}`;
      
      if (visited.has(key)) continue;
      if (x < 0 || x >= canvas.width || y < 0 || y >= canvas.height) continue;
      
      const currentColor = getPixelColor(currentPixels, x, y, canvas.width);
      
      // Vérifier si c'est une ligne noire (ne pas effacer les contours)
      if (isBlackLine(currentColor)) continue;
      
      if (!colorsMatch(currentColor, targetColor)) continue;
      
      visited.add(key);
      
      // Restaurer le pixel original
      const idx = (y * canvas.width + x) * 4;
      currentPixels[idx] = originalPixels[idx];
      currentPixels[idx + 1] = originalPixels[idx + 1];
      currentPixels[idx + 2] = originalPixels[idx + 2];
      currentPixels[idx + 3] = originalPixels[idx + 3];
      
      // Ajouter les pixels adjacents
      stack.push([x + 1, y]);
      stack.push([x - 1, y]);
      stack.push([x, y + 1]);
      stack.push([x, y - 1]);
    }

    ctx.putImageData(currentData, 0, 0);
  };

  // Utilitaires de couleur
  const getPixelColor = (pixels, x, y, width) => {
    const idx = (y * width + x) * 4;
    return {
      r: pixels[idx],
      g: pixels[idx + 1],
      b: pixels[idx + 2],
      a: pixels[idx + 3]
    };
  };

  const setPixelColor = (pixels, x, y, width, color) => {
    const idx = (y * width + x) * 4;
    pixels[idx] = color.r;
    pixels[idx + 1] = color.g;
    pixels[idx + 2] = color.b;
    pixels[idx + 3] = 255;
  };

  const hexToRgb = (hex) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16),
      a: 255
    } : { r: 0, g: 0, b: 0, a: 255 };
  };

  const colorsMatch = (c1, c2, tolerance = 10) => {
    return Math.abs(c1.r - c2.r) <= tolerance &&
           Math.abs(c1.g - c2.g) <= tolerance &&
           Math.abs(c1.b - c2.b) <= tolerance;
  };

  const isBlackLine = (color, threshold = 50) => {
    return color.r < threshold && color.g < threshold && color.b < threshold;
  };

  const isWhiteOrTransparent = (color, threshold = 240) => {
    return (color.r > threshold && color.g > threshold && color.b > threshold) || color.a < 10;
  };

  // Gestionnaire de clic sur le canvas
  const handleCanvasClick = (e) => {
    if (!imageLoaded) return;

    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = Math.floor((e.clientX - rect.left) * (canvas.width / rect.width));
    const y = Math.floor((e.clientY - rect.top) * (canvas.height / rect.height));

    if (tool === 'bucket') {
      floodFill(x, y, selectedColor);
    } else if (tool === 'eraser') {
      eraseArea(x, y);
    }
  };

  // Sauvegarder l'image coloriée
  const handleSave = () => {
    const canvas = canvasRef.current;
    canvas.toBlob((blob) => {
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `coloriage_colorie_${Date.now()}.png`;
      link.click();
      URL.revokeObjectURL(url);
    });
  };

  // Réinitialiser le coloriage
  const handleReset = () => {
    if (!ctx || !originalImageData) return;
    ctx.putImageData(originalImageData, 0, 0);
  };

  return (
    <div className="coloring-canvas-overlay">
      <div className="coloring-canvas-container">
        {/* Barre d'outils supérieure */}
        <div className="coloring-toolbar-top">
          <h2 className="coloring-canvas-title">🎨 Coloriez votre dessin</h2>
          <div className="coloring-toolbar-actions">
            <button className="coloring-btn coloring-reset-btn" onClick={handleReset} title="Réinitialiser">
              🔄 Réinitialiser
            </button>
            <button className="coloring-btn coloring-save-btn" onClick={handleSave} title="Télécharger">
              💾 Télécharger
            </button>
            <button className="coloring-btn coloring-close-btn-top" onClick={onClose} title="Fermer">
              ✕
            </button>
          </div>
        </div>

        {/* Zone de canvas */}
        <div className="coloring-canvas-wrapper">
          <canvas
            ref={canvasRef}
            onClick={handleCanvasClick}
            className="coloring-canvas"
          />
          {!imageLoaded && (
            <div className="coloring-loading">
              <div className="coloring-spinner"></div>
              <p>Chargement du coloriage...</p>
            </div>
          )}
        </div>

        {/* Barre d'outils inférieure */}
        <div className="coloring-toolbar-bottom">
          {/* Sélection d'outils */}
          <div className="coloring-tools">
            <button
              className={`coloring-tool-btn ${tool === 'bucket' ? 'active' : ''}`}
              onClick={() => setTool('bucket')}
              title="Seau de peinture"
            >
              🪣
            </button>
            <button
              className={`coloring-tool-btn ${tool === 'eraser' ? 'active' : ''}`}
              onClick={() => setTool('eraser')}
              title="Gomme"
            >
              🧹
            </button>
          </div>

          {/* Palette de couleurs */}
          <div className="coloring-palette">
            {colorPalette.map((color, index) => (
              <button
                key={index}
                className={`coloring-color-btn ${selectedColor === color && tool === 'bucket' ? 'active' : ''}`}
                style={{ backgroundColor: color }}
                onClick={() => {
                  setSelectedColor(color);
                  setTool('bucket');
                }}
                title={color}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ColoringCanvas;

