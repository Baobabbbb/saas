import React, { useRef, useEffect, useState } from 'react';
import './ColoringCanvas.css';

const ColoringCanvas = ({ imageUrl, theme, onClose, onSave }) => {
  const canvasRef = useRef(null);
  const [ctx, setCtx] = useState(null);
  const [selectedColor, setSelectedColor] = useState('#FF6B6B');
  const [tool, setTool] = useState('bucket'); // 'bucket' ou 'eraser'
  const [isZoomed, setIsZoomed] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [originalImageData, setOriginalImageData] = useState(null);
  const [coloringData, setColoringData] = useState(null);
  
  // Palette de couleurs enrichie inspirée de Happy Color
  const colorPalette = [
    // Rouges et roses
    '#FF6B6B', '#FF4757', '#FF6348', '#FFA07A', '#FF85C0', '#FFB6C1', '#FF1493', '#DC143C',
    // Oranges et jaunes
    '#F8B739', '#FFA500', '#FFD700', '#F7DC6F', '#FFDAB9', '#FFE4B5', '#F4A460', '#FDB813',
    // Verts
    '#52C41A', '#98D8C8', '#81C784', '#00C853', '#20B2AA', '#3CB371', '#90EE90', '#7FFF00',
    // Bleus et turquoises
    '#4ECDC4', '#45B7D1', '#85C1E9', '#A8DADC', '#00BFFF', '#1E90FF', '#4169E1', '#6495ED',
    // Violets et mauves
    '#BB8FCE', '#9B59B6', '#8B008B', '#DA70D6', '#E6E6FA', '#DDA0DD', '#BA55D3', '#9370DB',
    // Marrons et beiges
    '#DDA15E', '#BC6C25', '#D2691E', '#CD853F', '#8B4513', '#A0522D', '#F5DEB3', '#FAEBD7',
    // Gris et neutres
    '#95A5A6', '#7F8C8D', '#BDC3C7', '#ECF0F1', '#D3D3D3', '#C0C0C0', '#A9A9A9', '#808080',
    // Couleurs vives supplémentaires
    '#E07A5F', '#FF6B9D', '#00D9FF', '#FFEB3B', '#FF5722', '#8BC34A', '#00BCD4', '#E91E63'
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

      link.href = url; // Ajout de href manquant

      // Générer un nom de fichier cohérent basé sur le thème
      const themeName = theme || 'coloriage';
      const safeTheme = themeName.replace(/[^a-z0-9]/gi, '_').toLowerCase();
      link.download = `coloriages_${safeTheme}_colorie.png`;

      document.body.appendChild(link); // Ajout pour compatibilité
      link.click();
      document.body.removeChild(link); // Nettoyage
      URL.revokeObjectURL(url);
    });
  };

  // Gestion du clic sur l'overlay pour fermer
  const handleOverlayClick = (e) => {
    if (e.target.classList.contains('coloring-canvas-overlay')) {
      onClose();
    }
  };

  // Réinitialiser le coloriage
  const handleReset = () => {
    if (!ctx || !originalImageData) return;
    ctx.putImageData(originalImageData, 0, 0);
  };

  // Gestion du zoom
  const toggleZoom = () => {
    setIsZoomed(!isZoomed);
  };

  const zoomIn = () => {
    setZoomLevel(prev => Math.min(prev + 0.5, 3));
    setIsZoomed(true);
  };

  const zoomOut = () => {
    if (zoomLevel > 1) {
      setZoomLevel(prev => Math.max(prev - 0.5, 1));
      if (zoomLevel - 0.5 <= 1) {
        setIsZoomed(false);
      }
    }
  };

  return (
    <div className="coloring-canvas-overlay" onClick={handleOverlayClick}>
      <div className="coloring-canvas-container">
        {/* Barre d'outils supérieure */}
        <div className="coloring-toolbar-top">
          <h2 className="coloring-canvas-title">🎨 Coloriez votre dessin</h2>

          {/* Contrôles de zoom */}
          <div className="coloring-zoom-controls">
            <button
              className="coloring-zoom-btn"
              onClick={zoomOut}
              disabled={zoomLevel <= 1}
              title="Zoom arrière"
            >
              −
            </button>
            <span style={{ color: 'white', fontWeight: 'bold', minWidth: '60px', textAlign: 'center' }}>
              {Math.round(zoomLevel * 100)}%
            </span>
            <button
              className="coloring-zoom-btn"
              onClick={zoomIn}
              disabled={zoomLevel >= 3}
              title="Zoom avant"
            >
              +
            </button>
          </div>

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
            className={`coloring-canvas ${isZoomed ? 'zoomed' : ''}`}
            style={{ transform: `scale(${zoomLevel})` }}
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
              🧽
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

