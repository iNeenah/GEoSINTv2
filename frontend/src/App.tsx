import React, { useState } from 'react';
import './App.css';

// Definimos una interfaz para la estructura de la respuesta que esperamos
interface AnalysisResult {
  country: string;
  region_or_city: string;
  coordinates: string;
  confidence: string;
  reasoning: string;
}

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleAnalyzeClick = async () => {
    if (!selectedFile) {
      setError("Por favor, selecciona una imagen primero.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setAnalysis(null);

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      // Esta es la llamada a TU backend, no a Google.
      const response = await fetch('http://localhost:5001/api/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Error del servidor: ${response.statusText}`);
      }

      const data: AnalysisResult = await response.json();
      setAnalysis(data);

    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Geo OSINT Tool</h1>
        <input type="file" accept="image/*" onChange={handleFileChange} />
        <button onClick={handleAnalyzeClick} disabled={!selectedFile || isLoading}>
          {isLoading ? 'Analizando...' : 'Analizar Imagen'}
        </button>

        {error && <p style={{ color: 'red' }}>Error: {error}</p>}
        
        {analysis && (
          <div className="results">
            <h2>Resultados del Análisis</h2>
            <p><strong>País:</strong> {analysis.country}</p>
            <p><strong>Región/Ciudad:</strong> {analysis.region_or_city}</p>
            <p><strong>Coordenadas:</strong> {analysis.coordinates}</p>
            <p><strong>Confianza:</strong> {analysis.confidence}</p>
            <p><strong>Razonamiento:</strong> {analysis.reasoning}</p>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
