import React, { useState, useRef } from 'react';
import './App.css';

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
}

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [pasteHint, setPasteHint] = useState(false);
  const [isPasting, setIsPasting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      setSelectedFile(file);
      
      // Create preview URL
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      
      // Clear previous results
      setAnalysis(null);
      setError(null);
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const files = event.dataTransfer.files;
    if (files && files[0]) {
      const file = files[0];
      if (file.type.startsWith('image/')) {
        setSelectedFile(file);
        const url = URL.createObjectURL(file);
        setPreviewUrl(url);
        setAnalysis(null);
        setError(null);
      }
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const handlePaste = async (event: ClipboardEvent) => {
    const items = event.clipboardData?.items;
    if (!items) return;

    setIsPasting(true);
    
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile();
        if (file) {
          // Add a small delay for visual feedback
          setTimeout(() => {
            setSelectedFile(file);
            const url = URL.createObjectURL(file);
            setPreviewUrl(url);
            setAnalysis(null);
            setError(null);
            setPasteHint(false);
            setIsPasting(false);
          }, 300);
          break;
        }
      }
    }
    
    // Reset pasting state if no image was found
    setTimeout(() => setIsPasting(false), 300);
  };

  const handleKeyDown = (event: KeyboardEvent) => {
    // Show paste hint when Ctrl+V is pressed
    if (event.ctrlKey && event.key === 'v') {
      setPasteHint(true);
      setTimeout(() => setPasteHint(false), 2000);
    }
  };

  // Add event listeners for paste functionality
  React.useEffect(() => {
    document.addEventListener('paste', handlePaste);
    document.addEventListener('keydown', handleKeyDown);
    
    return () => {
      document.removeEventListener('paste', handlePaste);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  const handleAnalyzeClick = async () => {
    if (!selectedFile) {
      setError("Please select an image first.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setAnalysis(null);

    const formData = new FormData();
    formData.append('image', selectedFile);

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
  };

  const clearSelection = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setAnalysis(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="container">
          <div className="logo">
            <h1>GeoSINT</h1>
            <span className="version">v2.0</span>
          </div>
          <nav className="nav">
            <a href="#" className="nav-link">Documentation</a>
            <a href="#" className="nav-link">API</a>
            <a href="https://github.com/iNeenah/GEoSINTv2" className="nav-link">GitHub</a>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <h2 className="hero-title">
              AI-Powered Geospatial Intelligence
            </h2>
            <p className="hero-subtitle">
              Extract geographical information, architectural details, and location insights from images using advanced AI technology.
            </p>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main className="main">
        <div className="container">
          <div className="upload-section">
            <div 
              className={`upload-area ${selectedFile ? 'has-file' : ''} ${isPasting ? 'pasting' : ''}`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onClick={() => fileInputRef.current?.click()}
              tabIndex={0}
            >
              {!selectedFile ? (
                <div className="upload-placeholder">
                  <div className="upload-icon">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                      <polyline points="7,10 12,15 17,10"/>
                      <line x1="12" y1="15" x2="12" y2="3"/>
                    </svg>
                  </div>
                  <h3>Drop your image here</h3>
                  <p>or click to browse files</p>
                  <div className="upload-methods">
                    <div className="method-item">
                      <kbd>Ctrl</kbd> + <kbd>V</kbd>
                      <span>Paste from clipboard</span>
                    </div>
                    <div className="method-item">
                      <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>S</kbd>
                      <span>Screenshot & paste</span>
                    </div>
                  </div>
                  <span className="file-types">Supports JPG, PNG, GIF up to 10MB</span>
                  {pasteHint && (
                    <div className="paste-hint">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
                        <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
                      </svg>
                      Ready to paste image from clipboard
                    </div>
                  )}
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
                      <button onClick={clearSelection} className="clear-btn" title="Remove image">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <line x1="18" y1="6" x2="6" y2="18"/>
                          <line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                        Clear
                      </button>
                      <button onClick={() => fileInputRef.current?.click()} className="replace-btn" title="Replace with another image">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                          <polyline points="7,10 12,15 17,10"/>
                          <line x1="12" y1="15" x2="12" y2="3"/>
                        </svg>
                        Replace
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="file-input"
            />

            <div className="action-section">
              <button 
                onClick={handleAnalyzeClick} 
                disabled={!selectedFile || isLoading}
                className="analyze-btn"
              >
                {isLoading ? (
                  <>
                    <div className="spinner"></div>
                    Analyzing...
                  </>
                ) : (
                  'Analyze Image'
                )}
              </button>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="error-card">
              <div className="error-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="15" y1="9" x2="9" y2="15"/>
                  <line x1="9" y1="9" x2="15" y2="15"/>
                </svg>
              </div>
              <p>{error}</p>
            </div>
          )}

          {/* Results Display */}
          {analysis && (
            <div className="results-section">
              <div className="results-header">
                <h3>OSINT Analysis Results</h3>
                <div className="confidence-badge">
                  <span className="confidence-label">Confidence</span>
                  <span className="confidence-value">{analysis.confidence}</span>
                </div>
              </div>

              {/* Primary Location Info */}
              <div className="primary-location">
                <h4>Primary Location Assessment</h4>
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
                      <div className="location-item full-width">
                        <span className="label">Most Probable Location:</span>
                        <span className="value">{analysis.detailed_analysis.final_assessment.most_probable_location}</span>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Evidence Analysis */}
              {analysis.detailed_analysis?.evidence && (
                <div className="evidence-section">
                  <h4>Forensic Evidence Analysis</h4>
                  <div className="evidence-grid">
                    <div className="evidence-card">
                      <div className="evidence-icon">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                          <path d="M9 11H5a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7a2 2 0 0 0-2-2h-4"/>
                          <polyline points="9,11 12,14 15,11"/>
                          <line x1="12" y1="14" x2="12" y2="3"/>
                        </svg>
                      </div>
                      <div className="evidence-content">
                        <h5>Signage</h5>
                        <p>{analysis.detailed_analysis.evidence.signage}</p>
                      </div>
                    </div>

                    <div className="evidence-card">
                      <div className="evidence-icon">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                          <polyline points="9,22 9,12 15,12 15,22"/>
                        </svg>
                      </div>
                      <div className="evidence-content">
                        <h5>Infrastructure</h5>
                        <p>{analysis.detailed_analysis.evidence.infrastructure}</p>
                      </div>
                    </div>

                    <div className="evidence-card">
                      <div className="evidence-icon">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                        </svg>
                      </div>
                      <div className="evidence-content">
                        <h5>Architecture</h5>
                        <p>{analysis.detailed_analysis.evidence.architecture}</p>
                      </div>
                    </div>

                    <div className="evidence-card">
                      <div className="evidence-icon">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                        </svg>
                      </div>
                      <div className="evidence-content">
                        <h5>Environment</h5>
                        <p>{analysis.detailed_analysis.evidence.environment}</p>
                      </div>
                    </div>

                    <div className="evidence-card">
                      <div className="evidence-icon">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                          <circle cx="12" cy="12" r="3"/>
                          <path d="M12 1v6m0 6v6m11-7h-6m-6 0H1"/>
                        </svg>
                      </div>
                      <div className="evidence-content">
                        <h5>Cultural Elements</h5>
                        <p>{analysis.detailed_analysis.evidence.cultural_elements}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Alternative Locations */}
              {analysis.detailed_analysis?.alternative_locations && (
                <div className="alternatives-section">
                  <h4>Alternative Locations</h4>
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
                        </div>
                      )
                    ))}
                  </div>
                </div>
              )}

              {/* Full Analysis */}
              <div className="full-analysis-section">
                <h4>Complete Forensic Analysis</h4>
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