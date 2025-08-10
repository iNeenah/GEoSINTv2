# GeoSINT v2

A sophisticated geospatial intelligence tool that leverages Google's Gemini AI to analyze images and extract geographical information, architectural details, and location insights.

## Overview

GeoSINT v2 is a full-stack application designed for Open Source Intelligence (OSINT) practitioners, researchers, and analysts who need to identify geographical locations from images. The tool combines modern web technologies with advanced AI capabilities to provide detailed location analysis including coordinates, regional information, and contextual reasoning.

## Features

- **AI-Powered Analysis**: Utilizes Google Gemini Pro Vision for advanced image recognition
- **Geographical Intelligence**: Extracts country, region, and coordinate information
- **Architectural Recognition**: Identifies distinctive building styles and landmarks
- **Confidence Scoring**: Provides reliability metrics for analysis results
- **Modern Interface**: Clean, responsive React-based user interface
- **RESTful API**: Well-structured backend API for integration capabilities

## Architecture

```
GeoSINT v2/
├── frontend/                 # React + TypeScript + Vite
│   ├── src/
│   │   ├── App.tsx          # Main application component
│   │   ├── App.css          # Application styling
│   │   └── ...
│   ├── package.json
│   └── vite.config.ts
├── backend/                  # Python Flask API
│   ├── app.py               # Main Flask application
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables
│   └── test_api.py          # API testing utility
└── README.md
```

## Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Google Gemini API Key** (obtain from Google AI Studio)

## Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
   - Copy your Google Gemini API key
   - Ensure the `.env` file contains: `GEMINI_API_KEY=your_api_key_here`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

## Usage

### Starting the Application

1. **Start the Backend Server**:
```bash
cd backend
python app.py
```
The API server will be available at `http://localhost:5001`

2. **Start the Frontend Development Server**:
```bash
cd frontend
npm run dev
```
The web interface will be available at `http://localhost:5173`

### Using the Interface

1. Open your web browser and navigate to the frontend URL
2. Click "Choose File" to select an image for analysis
3. Click "Analizar Imagen" to begin the analysis process
4. Review the results including:
   - **Country**: Identified nation or territory
   - **Region/City**: Specific location details
   - **Coordinates**: Geographical coordinates when available
   - **Confidence**: Reliability score of the analysis
   - **Reasoning**: Detailed explanation of the identification process

## API Reference

### POST /api/analyze

Analyzes an uploaded image for geographical information.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Form data with `image` field containing the image file

**Response:**
```json
{
  "country": "Spain",
  "region_or_city": "Barcelona, Catalonia",
  "coordinates": "41.3851, 2.1734",
  "confidence": "High",
  "reasoning": "The architectural style shows typical Catalan modernist features..."
}
```

**Error Response:**
```json
{
  "error": "Error message description"
}
```

## Development

### Testing the API

Use the included test utility to verify backend functionality:

```bash
cd backend
python test_api.py
```

### Building for Production

**Frontend:**
```bash
cd frontend
npm run build
```

**Backend:**
For production deployment, consider using a WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

## Technology Stack

**Frontend:**
- React 19.1.1
- TypeScript 5.8.3
- Vite 7.1.0
- Modern CSS3

**Backend:**
- Python 3.8+
- Flask 3.1.1
- Google Generative AI 0.8.5
- Flask-CORS for cross-origin requests
- Pillow for image processing

**AI/ML:**
- Google Gemini Pro Vision
- Advanced computer vision capabilities
- Natural language processing for detailed analysis

## Security Considerations

- API keys are stored in environment variables
- CORS is configured for development (adjust for production)
- Input validation is implemented for file uploads
- Error handling prevents information leakage

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google AI team for the Gemini API
- Open source community for the underlying technologies
- OSINT community for inspiration and use cases

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/iNeenah/GEoSINTv2) or open an issue.