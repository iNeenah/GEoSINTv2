# 🌍 GeoSINT v2.0 - AI-Powered Geospatial Intelligence

<div align="center">

![GeoSINT Logo](https://img.shields.io/badge/GeoSINT-v2.0-blue?style=for-the-badge&logo=earth&logoColor=white)
![React](https://img.shields.io/badge/React-18.0-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=for-the-badge&logo=typescript&logoColor=white)

**Advanced OSINT tool for geolocation analysis using AI-powered image recognition**

[🚀 Live Demo](#) • [📖 Documentation](#setup) • [🐛 Report Bug](https://github.com/iNeenah/GEoSINTv2/issues) • [✨ Request Feature](https://github.com/iNeenah/GEoSINTv2/issues)

</div>

---

## ✨ Features

### 🤖 **AI-Powered Analysis**
- **Google Gemini Vision API** integration for intelligent image analysis
- **Advanced pattern recognition** for architectural and environmental elements
- **Confidence scoring** with detailed reasoning for each analysis

### 🔍 **Multiple Analysis Modes**
- **🎯 AI Analysis**: Standard OSINT analysis using Gemini Vision
- **🔎 Google Lens**: Web-based image matching for location identification  
- **📐 Multi-Angle Analysis**: Upload 2-6 images for 360° precision analysis

### 🗺️ **Interactive Mapping**
- **OpenStreetMap integration** with embedded maps
- **Google Maps & Street View** direct links
- **Coordinate copying** for external tools
- **Alternative locations** with confidence ratings

### 🔬 **Forensic Evidence Analysis**
- **Architectural analysis**: Building styles, materials, construction methods
- **Environmental factors**: Climate, vegetation, terrain analysis
- **Cultural elements**: Signage, language, regional indicators
- **Infrastructure assessment**: Roads, utilities, urban planning

### 🎨 **Modern UI/UX**
- **Glassmorphism design** inspired by modern web standards
- **Codrops text animations** with hover effects
- **Responsive design** for all devices
- **Dark theme** optimized for professional use

---

## 🛠️ Tech Stack

<div align="center">

| Frontend | Backend | AI/APIs | Styling |
|----------|---------|---------|---------|
| React 18 | Python 3.8+ | Google Gemini | Modern CSS |
| TypeScript | Flask | Google Lens API | Glassmorphism |
| Vite | CORS | Google Maps API | GSAP Animations |
| GSAP | Requests | OpenStreetMap | Inter Font |

</div>

---

## 🚀 Quick Start

### 📋 Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Google Cloud API key** with Gemini API access
- **Google Maps API key** (optional, for enhanced mapping)

### ⚡ Installation

1. **Clone the repository**
```bash
git clone https://github.com/iNeenah/GEoSINTv2.git
cd GEoSINTv2
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Environment Configuration**
```bash
# Create .env file in backend directory
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_CLOUD_API_KEY=your_google_cloud_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

4. **Frontend Setup**
```bash
cd ../frontend
npm install
```

5. **Start the Application**
```bash
# Terminal 1 - Backend
cd backend
python app.py

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

6. **Open your browser** to `http://localhost:5173`

---

## 📖 Usage Guide

### 🎯 **Analysis Modes**

#### **AI Analysis**
- Upload a single image
- Get comprehensive OSINT analysis
- Receive detailed forensic breakdown
- View confidence scores and reasoning

#### **Google Lens**
- Leverage web image matching
- Find similar images across the internet
- Identify landmarks and popular locations
- Cross-reference with online databases

#### **Multi-Angle Analysis**
- Upload 2-6 images of the same location
- Enhanced precision through multiple perspectives
- 360° analysis for comprehensive coverage
- Improved accuracy for complex locations

### 🗺️ **Results Interpretation**

- **Primary Location**: Most likely coordinates with confidence score
- **Alternative Locations**: Additional possibilities ranked by probability
- **Evidence Analysis**: Detailed breakdown of visual elements
- **Interactive Maps**: Explore results with multiple map services

---

## 🔧 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/analyze` | Single image AI analysis |
| `POST` | `/api/analyze-lens` | Google Lens image matching |
| `POST` | `/api/analyze-multi` | Multi-image analysis (2-6 images) |

### Request Format

```javascript
// Single Image Analysis
const formData = new FormData();
formData.append('image', imageFile);

fetch('/api/analyze', {
  method: 'POST',
  body: formData
});
```

### Response Format

```json
{
  "country": "United States",
  "region_or_city": "New York City",
  "coordinates": "40.7128, -74.0060",
  "confidence": "High (85%)",
  "reasoning": "Detailed analysis...",
  "detailed_analysis": {
    "primary_coordinates": {
      "lat": 40.7128,
      "lng": -74.0060
    },
    "evidence": {
      "signage": "English language signs...",
      "infrastructure": "Urban architecture...",
      "architecture": "Modern skyscrapers...",
      "environment": "Temperate climate..."
    }
  }
}
```

---

## 🎨 Design Features

### **Modern UI Elements**
- **Glassmorphism effects** with backdrop blur
- **Gradient overlays** and smooth transitions
- **Interactive hover states** with GSAP animations
- **Responsive grid layouts** for all screen sizes

### **Text Animations**
- **Codrops-inspired effects** with character morphing
- **Hover-triggered animations** for enhanced interactivity
- **Smooth transitions** with cubic-bezier easing
- **Professional typography** using Inter font family

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **🍴 Fork** the repository
2. **🌿 Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **💾 Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **📤 Push** to the branch (`git push origin feature/AmazingFeature`)
5. **🔄 Open** a Pull Request

### **Development Guidelines**
- Follow existing code style and conventions
- Add comments for complex logic
- Test your changes thoroughly
- Update documentation as needed

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

**Important**: This tool is designed for **educational and legitimate OSINT purposes only**. 

- Always respect **privacy laws** and regulations
- Follow **ethical guidelines** when conducting analysis
- Obtain **proper authorization** before analyzing images
- Use responsibly for **legitimate research** and investigation

---

## 🙏 Acknowledgments

- **Google Gemini API** for AI-powered image analysis
- **Codrops** for text animation inspiration
- **OpenStreetMap** for mapping services
- **React & TypeScript** communities for excellent tooling

---

<div align="center">

**Made with ❤️ for the OSINT community**

[⭐ Star this repo](https://github.com/iNeenah/GEoSINTv2) • [🐛 Report Issues](https://github.com/iNeenah/GEoSINTv2/issues) • [💬 Discussions](https://github.com/iNeenah/GEoSINTv2/discussions)

</div>