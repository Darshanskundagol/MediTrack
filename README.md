# MediTrack: Pharmacy Inventory Management with Expiry Risk Prediction

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-lightgrey.svg)](https://flask.palletsprojects.com/)

MediTrack is a comprehensive web-based pharmacy inventory management system built with Flask and machine learning capabilities. It helps pharmacies minimize drug wastage by predicting expiry risks, identifying slow-moving inventory, and providing actionable insights through interactive dashboards and reports.

## 🚀 Features

### Core Functionality
- **User Authentication**: Secure login/logout system with role-based access (Admin/Pharmacist)
- **Inventory Management**: Upload and manage pharmacy inventory data via CSV/Excel files
- **Expiry Risk Prediction**: Machine learning models to predict high-risk expiry items
- **Slow-Moving Detection**: Identify products with low turnover rates
- **Interactive Dashboard**: Real-time insights and visualizations
- **Comprehensive Reports**: Generate detailed reports with charts and analytics
- **Data Visualization**: Matplotlib/Seaborn-powered charts for trends and predictions

### Machine Learning Features
- **Predictive Analytics**: Uses scikit-learn models for expiry risk assessment
- **Data Preprocessing**: Automated cleaning and feature engineering
- **Model Training**: Customizable ML pipelines for inventory optimization
- **Batch Processing**: Handle large datasets efficiently

## 🛠️ Tech Stack

### Backend
- **Flask 3.0.3**: Web framework for routing, authentication, and API endpoints
- **Flask-SQLAlchemy 3.1.1**: ORM for database operations
- **Flask-Login 0.6.3**: User session management
- **Werkzeug 3.0.3**: WSGI utilities and security

### Data Science & ML
- **Pandas 3.0.2**: Data manipulation and analysis
- **NumPy 2.4.4**: Numerical computing
- **Scikit-Learn 1.8.0**: Machine learning algorithms
- **Joblib 1.4.2**: Model serialization
- **Matplotlib 3.10.9**: Data visualization
- **Seaborn 0.13.2**: Statistical visualization

### Frontend
- **HTML/CSS/JavaScript**: Responsive web interface
- **Bootstrap/Jinja2**: Templating and styling

### Deployment
- **Gunicorn 22.0.0**: Production WSGI server

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Darshanskundagol/Meditrack.git
   cd meditrack
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**
   ```bash
   python app.py
   ```
   This will create the SQLite database and seed the default admin user.

5. **Run the application**
   ```bash
   python app.py
   ```
   Open your browser and navigate to `http://localhost:5000`

### Default Credentials
- **Username**: admin
- **Password**: admin123

## 📖 Usage

### For Pharmacists
1. **Login** with your credentials
2. **Upload Inventory Data**: Use CSV/Excel files containing product information
3. **View Dashboard**: Monitor inventory status and predictions
4. **Generate Reports**: Analyze trends and download insights

### For Administrators
- Manage user accounts
- Configure system settings
- Access advanced analytics

### API Endpoints
- `GET /`: Home page
- `GET /login`: User login
- `GET /dashboard`: Main dashboard
- `POST /predict`: Upload and predict inventory risks
- `GET /reports`: View and download reports

## 🏗️ Project Structure

```
meditrack/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── extensions.py          # Flask extensions (DB, Login)
├── models_db.py           # SQLAlchemy database models
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── .gitignore             # Git ignore rules
├── LICENSE                # MIT License
├── dataset/               # Sample datasets
├── instance/              # Database files (ignored)
├── models/                # ML models and scripts
│   ├── preprocessing.py
│   ├── train_model.py
│   ├── predict.py
│   └── feature_engineering.py
├── routes/                # Flask blueprints
│   ├── auth.py
│   ├── dashboard.py
│   ├── prediction.py
│   └── reports.py
├── static/                # CSS, JS, Images
├── templates/             # HTML templates
├── uploads/               # User-uploaded files (ignored)
└── utils/                 # Utility functions
```

## 🤖 Machine Learning Pipeline

1. **Data Ingestion**: Upload CSV/Excel files
2. **Preprocessing**: Clean and normalize data
3. **Feature Engineering**: Create predictive features
4. **Model Training**: Train scikit-learn models
5. **Prediction**: Generate risk assessments
6. **Visualization**: Create charts and reports

## 📊 Sample Data

The `dataset/` folder contains sample pharmacy inventory data:
- `inventory_data.csv`: Product inventory
- `sales_data.csv`: Sales history
- `purchase_data.csv`: Purchase records

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production (with Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:create_app
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:create_app"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation
- Ensure all tests pass

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Darshanskundagol** - *Initial work* - [GitHub](https://github.com/Darshanskundagol)

## 🙏 Acknowledgments

- Flask community for the excellent web framework
- Scikit-learn for machine learning tools
- Open source contributors

## 📞 Support

If you have any questions or issues, please open an issue on GitHub or contact the maintainers.

---

**Made with ❤️ for pharmacy professionals**
