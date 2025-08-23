import React, { useState, useRef, useEffect } from 'react';
import './App.css';
import TextAnimator from './components/TextAnimator';

interface AnalysisResult {
  country: string;
  region_or_city: string;
  coordinates: string;
  confidence: string;
  reasoning: string;
  detailed_analysis?: {
    primary_coordinates: {
      lat: number | null;
      lng: number | null;
    };
    alternative_locations: Array<{
      lat: number | null;
      lng: number | null;
    }>;
    evidence: {
      signage: string;
      infrastructure: string;
      architecture: string;
      environment: string;
      cultural_elements: string;
    };
    final_assessment: {
      most_probable_location: string;
      certainty_percentage: number;
      primary_landmark: string;
    };
  };
  multi_image_analysis?: {
    total_images: number;
    analysis_type: string;
  };
}

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [previewUrls, setPreviewUrls] = useState<string[]>([]);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [analysisMode, setAnalysisMode] = useState<'single' | 'multi' | 'lens'>('single');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const multiFileInputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [showPasteHint, setShowPasteHint] = useState(false);



  // Función para manejar pegado desde portapapeles
  const handlePaste = async (event: ClipboardEvent) => {
    event.preventDefault();
    const items = event.clipboardData?.items;
    
    if (!items) return;
    
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      
      if (item.type.indexOf('image') !== -1) {
        const file = item.getAsFile();
        if (file) {
          if (analysisMode === 'single' || analysisMode === 'lens') {
            setSelectedFile(file);
            const url = URL.createObjectURL(file);
            setPreviewUrl(url);
            setAnalysis(null);
            setError(null);
          } else {
            // Para modo multi, agregar a la lista existente
            const newFiles = [...selectedFiles, file];
            if (newFiles.length > 6) {
              setError("Máximo 6 imágenes permitidas para análisis multi-angular");
              return;
            }
            
            setSelectedFiles(newFiles);
            const newUrls = [...previewUrls, URL.createObjectURL(file)];
            setPreviewUrls(newUrls);
            setAnalysis(null);
            setError(null);
          }
          
          // Mostrar notificación de éxito
          setShowPasteHint(true);
          setTimeout(() => setShowPasteHint(false), 2000);
        }
        break;
      }
    }
  };

  // Función para manejar drag and drop
  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(event.dataTransfer.files);
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    
    if (imageFiles.length === 0) {
      setError("Por favor, arrastra solo archivos de imagen");
      return;
    }
    
    if (analysisMode === 'single' || analysisMode === 'lens') {
      const file = imageFiles[0];
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      setAnalysis(null);
      setError(null);
    } else {
      const newFiles = [...selectedFiles, ...imageFiles];
      if (newFiles.length > 6) {
        setError("Máximo 6 imágenes permitidas para análisis multi-angular");
        return;
      }
      
      setSelectedFiles(newFiles);
      const newUrls = [...previewUrls, ...imageFiles.map(file => URL.createObjectURL(file))];
      setPreviewUrls(newUrls);
      setAnalysis(null);
      setError(null);
    }
  };

  // Efecto para agregar event listeners globales
  useEffect(() => {
    const handleGlobalPaste = (event: ClipboardEvent) => {
      // Solo activar si estamos en las áreas de upload
      if (document.activeElement?.closest('.upload-section') || 
          document.activeElement?.closest('.upload-area') ||
          document.activeElement?.closest('.multi-upload-area')) {
        handlePaste(event);
      }
    };

    const handleGlobalKeyDown = (event: KeyboardEvent) => {
      // Mostrar hint cuando se presiona Ctrl+V
      if (event.ctrlKey && event.key === 'v') {
        setShowPasteHint(true);
        setTimeout(() => setShowPasteHint(false), 1500);
      }
    };

    document.addEventListener('paste', handleGlobalPaste);
    document.addEventListener('keydown', handleGlobalKeyDown);
    
    return () => {
      document.removeEventListener('paste', handleGlobalPaste);
      document.removeEventListener('keydown', handleGlobalKeyDown);
    };
  }, [analysisMode, selectedFiles, previewUrls]);

  const openInGoogleMaps = (lat: number, lng: number) => {
    const url = `https://www.google.com/maps/search/?api=1&query=${lat},${lng}`;
    window.open(url, '_blank');
  };

  const openInGoogleStreetView = (lat: number, lng: number) => {
    const url = `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat},${lng}`;
    window.open(url, '_blank');
  };

  const copyCoordinates = (lat: number, lng: number) => {
    const coords = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    navigator.clipboard.writeText(coords);
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      setAnalysis(null);
      setError(null);
    }
  };

  const handleMultiFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      const files = Array.from(event.target.files);
      
      if (files.length > 6) {
        setError("Maximum 6 images allowed for multi-angle analysis");
        return;
      }
      
      if (files.length < 2) {
        setError("Minimum 2 images required for multi-angle analysis");
        return;
      }
      
      setSelectedFiles(files);
      const urls = files.map(file => URL.createObjectURL(file));
      setPreviewUrls(urls);
      setAnalysis(null);
      setError(null);
    }
  };

  const removeImage = (index: number) => {
    const updatedFiles = selectedFiles.filter((_, i) => i !== index);
    const updatedUrls = previewUrls.filter((_, i) => i !== index);
    
    URL.revokeObjectURL(previewUrls[index]);
    setSelectedFiles(updatedFiles);
    setPreviewUrls(updatedUrls);
    
    if (updatedFiles.length < 2) {
      setError("Minimum 2 images required for multi-angle analysis");
    } else {
      setError(null);
    }
  };

  const handleAnalyzeClick = async () => {
    if (analysisMode === 'single' || analysisMode === 'lens') {
      if (!selectedFile) {
        setError("Please select an image first.");
        return;
      }
    } else {
      if (selectedFiles.length < 2) {
        setError("Please select at least 2 images for multi-angle analysis.");
        return;
      }
    }

    setIsLoading(true);
    setError(null);
    setAnalysis(null);

    const formData = new FormData();
    
    if (analysisMode === 'single') {
      formData.append('image', selectedFile!);
      
      try {
        const response = await fetch('http://localhost:5001/api/analyze', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Server error: ${response.statusText}`);
        }

        const data: AnalysisResult = await response.json();
        setAnalysis(data);

      } catch (err: any) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    } else if (analysisMode === 'lens') {
      formData.append('image', selectedFile!);
      
      try {
        const response = await fetch('http://localhost:5001/api/analyze-lens', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Server error: ${response.statusText}`);
        }

        const data: AnalysisResult = await response.json();
        setAnalysis(data);

      } catch (err: any) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    } else {
      selectedFiles.forEach((file) => {
        formData.append('images', file);
      });
      
      try {
        const response = await fetch('http://localhost:5001/api/analyze-multi', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Server error: ${response.statusText}`);
        }

        const data: AnalysisResult = await response.json();
        setAnalysis(data);

      } catch (err: any) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const clearSelection = () => {
    if (analysisMode === 'single' || analysisMode === 'lens') {
      setSelectedFile(null);
      setPreviewUrl(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } else {
      previewUrls.forEach(url => URL.revokeObjectURL(url));
      setSelectedFiles([]);
      setPreviewUrls([]);
      if (multiFileInputRef.current) {
        multiFileInputRef.current.value = '';
      }
    }
    
    setAnalysis(null);
    setError(null);
  };

  const switchMode = (mode: 'single' | 'multi' | 'lens') => {
    clearSelection();
    setAnalysisMode(mode);
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="container">
          <div className="header-brand">
            <div className="logo">
              <TextAnimator 
                className="logo-text" 
                trigger="hover"
                colors={['#667eea', '#764ba2', '#f093fb', '#4facfe']}
              >
                GeoSINT
              </TextAnimator>
              <span className="logo-badge">AI</span>
            </div>
            <div className="header-description">
              <TextAnimator 
                trigger="hover"
                colors={['#ffffff', '#667eea', '#f093fb']}
              >
                Powered by Advanced Geolocation Intelligence
              </TextAnimator>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <div className="hero-title">
              <TextAnimator 
                trigger="auto"
                delay={1000}
                colors={['#ffffff', '#667eea', '#764ba2', '#f093fb']}
              >
                <h2>AI-Powered Geospatial Intelligence</h2>
              </TextAnimator>
            </div>
            <p className="hero-subtitle">
              Extract geographical information, architectural details, and location insights from images using advanced AI technology.
            </p>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main className="main">
        <div className="container">
          {/* Analysis Mode Selector */}
          <div className="mode-selector">
            <div className="mode-selector-title">
              <TextAnimator 
                trigger="hover"
                colors={['#667eea', '#764ba2', '#f093fb']}
              >
                <h3>Analysis Mode</h3>
              </TextAnimator>
            </div>
            <div className="mode-buttons">
              <button 
                className={`mode-btn ${analysisMode === 'single' ? 'active' : ''}`}
                onClick={() => switchMode('single')}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <rect x="3" y="3" width="18" height="18" rx="3" ry="3"/>
                  <circle cx="9" cy="9" r="2"/>
                  <path d="M21 15l-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>
                </svg>
                <div className="mode-info">
                  <TextAnimator 
                    className="mode-title" 
                    trigger="hover"
                    colors={['#667eea', '#f093fb']}
                  >
                    AI Analysis
                  </TextAnimator>
                  <span className="mode-desc">Standard OSINT analysis</span>
                </div>
              </button>
              
              <button 
                className={`mode-btn ${analysisMode === 'lens' ? 'active' : ''}`}
                onClick={() => switchMode('lens')}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="11" cy="11" r="8"/>
                  <path d="M21 21l-4.35-4.35"/>
                  <circle cx="11" cy="11" r="3"/>
                </svg>
                <div className="mode-info">
                  <TextAnimator 
                    className="mode-title" 
                    trigger="hover"
                    colors={['#667eea', '#f093fb']}
                  >
                    Google Lens
                  </TextAnimator>
                  <span className="mode-desc">Web image matching</span>
                </div>
              </button>
              
              <button 
                className={`mode-btn ${analysisMode === 'multi' ? 'active' : ''}`}
                onClick={() => switchMode('multi')}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <rect x="3" y="3" width="7" height="7" rx="1"/>
                  <rect x="14" y="3" width="7" height="7" rx="1"/>
                  <rect x="14" y="14" width="7" height="7" rx="1"/>
                  <rect x="3" y="14" width="7" height="7" rx="1"/>
                </svg>
                <div className="mode-info">
                  <TextAnimator 
                    className="mode-title" 
                    trigger="hover"
                    colors={['#667eea', '#f093fb']}
                  >
                    Multi-Angle Analysis
                  </TextAnimator>
                  <span className="mode-desc">360° precision with 2-6 images</span>
                </div>
              </button>
            </div>
          </div>

          <div className="upload-section">
            {/* Notificación de pegado */}
            {showPasteHint && (
              <div className="paste-notification">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
                  <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
                  <path d="9 14l2 2 4-4"/>
                </svg>
                <span>¡Imagen pegada desde portapapeles!</span>
              </div>
            )}
            
            {analysisMode === 'single' || analysisMode === 'lens' ? (
              <div 
                className={`upload-area ${selectedFile ? 'has-file' : ''} ${isDragOver ? 'drag-over' : ''}`}
                onClick={() => fileInputRef.current?.click()}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                tabIndex={0}
              >
                {!selectedFile ? (
                  <div className="upload-placeholder">
                    <div className="upload-icon">
                      <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                        <polyline points="7,10 12,15 17,10"/>
                        <line x1="12" y1="15" x2="12" y2="3"/>
                      </svg>
                    </div>
                    <h3>{analysisMode === 'lens' ? 'Drop your image for Google Lens analysis' : 'Drop your image here'}</h3>
                    <p>{analysisMode === 'lens' ? 'Find this location on the web' : 'or click to browse files'}</p>
                    <div className="upload-methods">
                      <span className="file-types">
                        {analysisMode === 'lens' 
                          ? 'Google Lens will search billions of web images • JPG, PNG, GIF' 
                          : 'Supports JPG, PNG, GIF up to 10MB'
                        }
                      </span>
                      <div className="paste-hint">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
                          <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
                        </svg>
                        <span>o presiona Ctrl+V para pegar</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="file-preview">
                    {previewUrl && (
                      <img src={previewUrl} alt="Preview" className="preview-image" />
                    )}
                    <div className="file-info">
                      <h4>{selectedFile.name}</h4>
                      <p>{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                      <div className="file-actions">
                        <button onClick={clearSelection} className="clear-btn">
                          Clear
                        </button>
                        <button onClick={() => fileInputRef.current?.click()} className="replace-btn">
                          Replace
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div 
                className={`multi-upload-area ${isDragOver ? 'drag-over' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                tabIndex={0}
              >
                <div className="multi-upload-header">
                  <h3>Multi-Angle Analysis</h3>
                  <p>Upload 2-6 images of the same location from different angles for enhanced precision</p>
                </div>
                
                {selectedFiles.length === 0 ? (
                  <div 
                    className="upload-area multi-empty"
                    onClick={() => multiFileInputRef.current?.click()}
                  >
                    <div className="upload-icon">
                      <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                        <rect x="3" y="3" width="7" height="7" rx="1"/>
                        <rect x="14" y="3" width="7" height="7" rx="1"/>
                        <rect x="14" y="14" width="7" height="7" rx="1"/>
                        <rect x="3" y="14" width="7" height="7" rx="1"/>
                      </svg>
                    </div>
                    <h3>Select Multiple Images</h3>
                    <p>Choose 2-6 images of the same location</p>
                    <div className="upload-methods">
                      <span className="file-types">Different angles • Same location • JPG, PNG, GIF</span>
                      <div className="paste-hint">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
                          <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
                        </svg>
                        <span>o presiona Ctrl+V para pegar más imágenes</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="multi-preview-grid">
                    {previewUrls.map((url, index) => (
                      <div key={index} className="multi-preview-item">
                        <img src={url} alt={`Preview ${index + 1}`} className="multi-preview-image" />
                        <div className="multi-preview-info">
                          <span className="image-number">Image {index + 1}</span>
                          <button 
                            onClick={() => removeImage(index)} 
                            className="remove-image-btn"
                          >
                            ×
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                
                <div className="multi-upload-actions">
                  <button 
                    onClick={() => multiFileInputRef.current?.click()} 
                    className="multi-select-btn"
                  >
                    {selectedFiles.length === 0 ? 'Select Images' : 'Add More Images'}
                  </button>
                  
                  {selectedFiles.length > 0 && (
                    <button onClick={clearSelection} className="clear-all-btn">
                      Clear All
                    </button>
                  )}
                </div>
              </div>
            )}

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="file-input"
            />
            
            <input
              ref={multiFileInputRef}
              type="file"
              accept="image/*"
              multiple
              onChange={handleMultiFileChange}
              className="file-input"
            />

            <div className="action-section">
              <button 
                onClick={handleAnalyzeClick} 
                disabled={
                  ((analysisMode === 'single' || analysisMode === 'lens') && !selectedFile) || 
                  (analysisMode === 'multi' && selectedFiles.length < 2) || 
                  isLoading
                }
                className="analyze-btn"
              >
                {isLoading ? (
                  <>
                    <div className="spinner"></div>
                    {analysisMode === 'single' ? 'Analyzing...' : 
                     analysisMode === 'lens' ? 'Searching web images...' :
                     `Analyzing ${selectedFiles.length} images...`}
                  </>
                ) : (
                  <>
                    {analysisMode === 'single' ? 'Analyze Image' : 
                     analysisMode === 'lens' ? (
                       <>
                         <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                           <circle cx="11" cy="11" r="8"/>
                           <path d="M21 21l-4.35-4.35"/>
                         </svg>
                         Google Lens Search
                       </>
                     ) : 
                     `Analyze ${selectedFiles.length} Images (360° Mode)`}
                  </>
                )}
              </button>
              
              {analysisMode === 'multi' && selectedFiles.length > 0 && (
                <div className="analysis-info">
                  <div className="info-item">
                    <span className="info-label">Images:</span>
                    <span className="info-value">{selectedFiles.length}/6</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Mode:</span>
                    <span className="info-value">Multi-Angle Precision</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="error-card">
              <p>{error}</p>
            </div>
          )}

          {/* Results Display */}
          {analysis && (
            <div className="results-section">
              <div className="results-header">
                <div className="results-title">
                  <TextAnimator 
                    trigger="auto"
                    delay={500}
                    colors={['#667eea', '#764ba2', '#f093fb']}
                  >
                    <h3>OSINT Analysis Results</h3>
                  </TextAnimator>
                </div>
                <div className="confidence-badge">
                  <span className="confidence-label">Confidence</span>
                  <span className="confidence-value">{analysis.confidence}</span>
                </div>
              </div>

              {/* Primary Location Info */}
              <div className="primary-location">
                <div className="section-title">
                  <TextAnimator 
                    trigger="hover"
                    colors={['#667eea', '#f093fb']}
                  >
                    <h4>Primary Location Assessment</h4>
                  </TextAnimator>
                </div>
                <div className="location-grid">
                  <div className="location-item">
                    <span className="label">Country:</span>
                    <span className="value">{analysis.country}</span>
                  </div>
                  <div className="location-item">
                    <span className="label">Region/City:</span>
                    <span className="value">{analysis.region_or_city}</span>
                  </div>
                  <div className="location-item">
                    <span className="label">Coordinates:</span>
                    <span className="value coordinates">{analysis.coordinates}</span>
                  </div>
                  {analysis.detailed_analysis?.final_assessment && (
                    <>
                      <div className="location-item">
                        <span className="label">Certainty:</span>
                        <span className="value">{analysis.detailed_analysis.final_assessment.certainty_percentage}%</span>
                      </div>
                      <div className="location-item">
                        <span className="label">Primary Landmark:</span>
                        <span className="value">{analysis.detailed_analysis.final_assessment.primary_landmark}</span>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Location Map & Actions */}
              {analysis.detailed_analysis?.primary_coordinates?.lat && analysis.detailed_analysis?.primary_coordinates?.lng && (
                <div className="map-section">
                  <div className="map-header">
                    <div className="section-title">
                      <TextAnimator 
                        trigger="hover"
                        colors={['#667eea', '#f093fb']}
                      >
                        <h4>Location Visualization</h4>
                      </TextAnimator>
                    </div>
                    <div className="map-actions">
                      <button 
                        onClick={() => openInGoogleMaps(
                          analysis.detailed_analysis!.primary_coordinates.lat!, 
                          analysis.detailed_analysis!.primary_coordinates.lng!
                        )}
                        className="map-btn google-maps-btn"
                      >
                        Google Maps
                      </button>
                      <button 
                        onClick={() => openInGoogleStreetView(
                          analysis.detailed_analysis!.primary_coordinates.lat!, 
                          analysis.detailed_analysis!.primary_coordinates.lng!
                        )}
                        className="map-btn street-view-btn"
                      >
                        Street View
                      </button>
                      <button 
                        onClick={() => copyCoordinates(
                          analysis.detailed_analysis!.primary_coordinates.lat!, 
                          analysis.detailed_analysis!.primary_coordinates.lng!
                        )}
                        className="map-btn copy-btn"
                      >
                        Copy Coords
                      </button>
                    </div>
                  </div>
                  
                  <div className="map-container">
                    <iframe
                      src={`https://www.openstreetmap.org/export/embed.html?bbox=${analysis.detailed_analysis.primary_coordinates.lng - 0.01},${analysis.detailed_analysis.primary_coordinates.lat - 0.01},${analysis.detailed_analysis.primary_coordinates.lng + 0.01},${analysis.detailed_analysis.primary_coordinates.lat + 0.01}&layer=mapnik&marker=${analysis.detailed_analysis.primary_coordinates.lat},${analysis.detailed_analysis.primary_coordinates.lng}`}
                      width="100%"
                      height="400"
                      style={{ border: 0, borderRadius: '8px' }}
                      allowFullScreen
                      loading="lazy"
                      title="Location Map"
                    />
                  </div>
                </div>
              )}

              {/* Evidence Analysis */}
              {analysis.detailed_analysis?.evidence && (
                <div className="evidence-section">
                  <div className="section-title">
                    <TextAnimator 
                      trigger="hover"
                      colors={['#667eea', '#f093fb']}
                    >
                      <h4>Forensic Evidence Analysis</h4>
                    </TextAnimator>
                  </div>
                  <div className="evidence-grid">
                    <div className="evidence-card">
                      <h5>Signage</h5>
                      <p>{analysis.detailed_analysis.evidence.signage}</p>
                    </div>
                    <div className="evidence-card">
                      <h5>Infrastructure</h5>
                      <p>{analysis.detailed_analysis.evidence.infrastructure}</p>
                    </div>
                    <div className="evidence-card">
                      <h5>Architecture</h5>
                      <p>{analysis.detailed_analysis.evidence.architecture}</p>
                    </div>
                    <div className="evidence-card">
                      <h5>Environment</h5>
                      <p>{analysis.detailed_analysis.evidence.environment}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Alternative Locations */}
              {analysis.detailed_analysis?.alternative_locations && (
                <div className="alternatives-section">
                  <div className="section-title">
                    <TextAnimator 
                      trigger="hover"
                      colors={['#667eea', '#f093fb']}
                    >
                      <h4>Alternative Locations</h4>
                    </TextAnimator>
                  </div>
                  <div className="alternatives-grid">
                    {analysis.detailed_analysis.alternative_locations.map((location, index) => (
                      location.lat && location.lng && (
                        <div key={index} className="alternative-card">
                          <div className="alternative-header">
                            <span className="alternative-label">Alternative {index + 1}</span>
                          </div>
                          <div className="alternative-coords">
                            {location.lat.toFixed(6)}, {location.lng.toFixed(6)}
                          </div>
                          <div className="alternative-actions">
                            <button 
                              onClick={() => openInGoogleMaps(location.lat!, location.lng!)}
                              className="alt-btn"
                            >
                              Maps
                            </button>
                            <button 
                              onClick={() => openInGoogleStreetView(location.lat!, location.lng!)}
                              className="alt-btn"
                            >
                              Street View
                            </button>
                            <button 
                              onClick={() => copyCoordinates(location.lat!, location.lng!)}
                              className="alt-btn"
                            >
                              Copy
                            </button>
                          </div>
                        </div>
                      )
                    ))}
                  </div>
                </div>
              )}

              {/* Full Analysis */}
              <div className="full-analysis-section">
                <div className="section-title">
                  <TextAnimator 
                    trigger="hover"
                    colors={['#667eea', '#f093fb']}
                  >
                    <h4>Complete Forensic Analysis</h4>
                  </TextAnimator>
                </div>
                <div className="analysis-content">
                  <pre>{analysis.reasoning}</pre>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <p>Powered by Google Gemini AI • Built for OSINT professionals</p>
        </div>
      </footer>
    </div>
  );
}

export default App;