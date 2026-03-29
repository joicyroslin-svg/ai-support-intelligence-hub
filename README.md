# AI Support Intelligence Hub

🚀 **Advanced AI-powered support analytics dashboard with premium Figma-style design and agent building capabilities**

![Streamlit App](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-2563eb?style=for-the-badge&logo=Plotly&logoColor=white)
![Streamlit Cloud](https://img.shields.io/badge/Streamlit%20Cloud-29B09D?style=for-the-badge&logo=Streamlit&logoColor=white)

## 🌟 Features

### 🤖 **AI-Powered Analytics**
- **Smart Ticket Analysis**: Automatic priority, sentiment, and category classification
- **Bulk Processing**: Analyze multiple tickets simultaneously with AI insights
- **Historical Insights**: Trend analysis and pattern recognition from past tickets

### 🎨 **Premium Figma-Style Design**
- **Glassmorphism Effects**: Modern, translucent UI elements with blur effects
- **Gradient Themes**: Professional color schemes with smooth transitions
- **Dark Mode Support**: Complete theme switching with CSS-in-JS implementation
- **Responsive Design**: Optimized for all screen sizes

### 🤖 **Agent Builder**
- **Custom Agent Creation**: Build specialized AI support agents
- **Tool Integration**: Configure multiple LLM models and tools
- **JSON Configuration**: Export agent configurations for external use
- **Goal-Based Building**: Define specific agent purposes and functions

### 📊 **Advanced Analytics**
- **Real-time Metrics**: Live dashboard with key performance indicators
- **Interactive Charts**: Plotly-powered visualizations with drill-down capabilities
- **Priority Distribution**: Visual breakdown of ticket urgency levels
- **Category Analysis**: Department-wise ticket categorization

### 🔧 **Professional Features**
- **CSV Import/Export**: Seamless data integration and backup
- **Sample Data Seeding**: Quick start with realistic test data
- **Search & Filter**: Advanced filtering by priority, category, and keywords
- **Escalation Alerts**: Automatic highlighting of urgent tickets

## 🚀 Quick Start

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/joicyroslin-svg/ai-support-intelligence-hub.git
   cd ai-support-intelligence-hub
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the dashboard:**
   ```bash
   streamlit run ai_support_dashboard.py
   ```

5. **Access the application:**
   Open http://localhost:8501 in your browser

### Live Demo

🌐 **[View Live Demo](https://ai-support-intelligence-app-23.streamlit.app/)**

## 📋 Requirements

- Python 3.9+
- Streamlit 1.35+
- Plotly 5.17+
- LiteLLM 1.72+
- Pandas, NumPy, Requests

See `requirements.txt` for the complete list of dependencies.

## 🏗️ Architecture

```
ai-support-intelligence-hub/
├── ai_support_dashboard.py      # Main Streamlit application
├── assistant/                   # Core AI functionality
│   ├── agent.py                # Agent orchestration
│   ├── build_agent.py          # Agent builder logic
│   ├── config.py               # Configuration management
│   ├── llm.py                  # LLM client abstraction
│   ├── rag.py                  # Retrieval-Augmented Generation
│   ├── service.py              # Core service functions
│   └── ui_theme.py             # Theme management
├── data/                       # Sample data
│   └── sample_tickets.csv      # Example ticket data
├── tests/                      # Unit tests
└── requirements.txt            # Python dependencies
```

## 🎯 Usage

### 1. **Dashboard Overview**
- View real-time analytics and key metrics
- Monitor ticket volume, sentiment trends, and priority distribution
- Access escalation alerts for urgent tickets

### 2. **Ticket Management**
- Upload CSV files for bulk ticket analysis
- Filter tickets by priority, category, and keywords
- View tickets in table or chat format
- Bulk analyze filtered tickets with AI

### 3. **Single Ticket Analysis**
- Analyze individual tickets with AI
- Get priority, sentiment, and category classification
- Generate AI responses with different tones
- View similar historical tickets

### 4. **Agent Builder**
- Create custom AI support agents
- Configure tools and goals
- Export agent configurations as JSON
- Integrate with external systems

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# LLM Configuration
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
ANTHROPIC_API_KEY=your_claude_key_here

# Application Settings
DEFAULT_MODEL=gpt-4o-mini
MAX_OUTPUT_TOKENS=1000
TEMPERATURE=0.2
```

### Customization

- **Theme Colors**: Modify CSS variables in `assistant/ui_theme.py`
- **Default Models**: Update `DEFAULT_MODEL` in `assistant/config.py`
- **Analysis Settings**: Adjust parameters in `assistant/service.py`

## 🧪 Testing

Run the test suite:

```bash
pytest
```

Run specific tests:

```bash
pytest tests/test_service.py
pytest tests/test_llm.py
```

## 🚀 Deployment

### Streamlit Cloud (Recommended)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud:**
   - Go to https://streamlit.io/cloud
   - Connect your GitHub repository
   - Select `ai_support_dashboard.py` as the main file
   - Deploy!

3. **Your app will be live at:**
   `https://your-username-ai-support-hub.streamlit.app`

### Docker Deployment

```bash
# Build the image
docker build -t ai-support-hub .

# Run the container
docker run -p 8501:8501 ai-support-hub
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit** - For the amazing web framework
- **Plotly** - For beautiful interactive charts
- **LiteLLM** - For unified LLM API access
- **Figma** - For design inspiration

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/joicyroslin-svg/ai-support-intelligence-hub/issues)
- **Documentation**: [Wiki](https://github.com/joicyroslin-svg/ai-support-intelligence-hub/wiki)
- **Email**: [joicyroslin@example.com](mailto:joicyroslin@example.com)

---

**Made with ❤️ using Streamlit and AI**

[![GitHub stars](https://img.shields.io/github/stars/joicyroslin-svg/ai-support-intelligence-hub?style=social)](https://github.com/joicyroslin-svg/ai-support-intelligence-hub/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/joicyroslin-svg/ai-support-intelligence-hub?style=social)](https://github.com/joicyroslin-svg/ai-support-intelligence-hub/network/members)