# ✈️ Airbnb & Food Hunter

A Streamlit web application that helps you find accommodations and discover nearby restaurants using MongoDB's powerful **GeoSpatial Indexing** capabilities.

## 🌟 Features

- **Interactive Map Visualization**: View your selected apartment and nearby restaurants on an interactive map
- **GeoSpatial Queries**: Find restaurants within a customizable radius using MongoDB's `$near` operator
- **Color-Coded Markers**: Each restaurant is represented by a unique color on the map for easy identification
- **Dual Search Modes**:
  - Predefined list of popular accommodations
  - Custom search to find any apartment by name
- **Adjustable Search Radius**: Slider to control the distance range (0.5km - 5km)
- **Detailed Information**: View apartment details including type, bedrooms, and price

## 🛠️ Technologies Used

- **Python 3.12**
- **Streamlit**: Web application framework
- **MongoDB**: NoSQL database with GeoSpatial indexing
- **PyMongo**: MongoDB driver for Python
- **Pandas**: Data manipulation and analysis

## 📋 Prerequisites

- Python 3.12 or higher
- MongoDB running locally on `localhost:27017`
- Virtual environment (recommended)

## 🚀 Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd Projet
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
```

3. **Install dependencies**
```bash
pip install streamlit pymongo pandas
```

4. **Set up MongoDB indexes**

Run the setup script to create the necessary GeoSpatial indexes:
```bash
python setup_indexes.py
```

This will create 2dsphere indexes on:
- `listings.address.location`
- `restaurants.address.coord`

## 💾 Database Structure

### Database: `geoloca`

#### Collections:

**listings** (5555 documents)
```javascript
{
  name: "Private Room in Bushwick",
  property_type: "Apartment",
  bedrooms: 2,
  price: "$50",
  address: {
    location: {
      type: "Point",
      coordinates: [longitude, latitude]  // [lon, lat] format
    }
  }
}
```

**restaurants** (3772 documents)
```javascript
{
  name: "Morris Park Bake Shop",
  cuisine: "Bakery",
  address: {
    coord: [longitude, latitude]  // [lon, lat] format
  },
  grades: [...]
}
```

## 🎮 Usage

1. **Start the application**
```bash
streamlit run app.py
```

2. **Open your browser**
Navigate to `http://localhost:8502`

3. **Select an apartment**
   - Choose from the predefined list, or
   - Use custom search to find any apartment

4. **Explore restaurants**
   - Adjust the search radius slider
   - View restaurants in the table with color codes
   - See all locations on the interactive map

## 🗺️ GeoSpatial Query Example

The application uses MongoDB's `$near` operator to find restaurants:

```javascript
db.restaurants.find({
  "address.coord": {
    $near: {
      $geometry: {
        type: "Point",
        coordinates: [lon, lat]
      },
      $maxDistance: 1000  // in meters
    }
  }
})
```

## 📁 Project Structure

```
Projet/
├── app.py                 # Main Streamlit application
├── setup_indexes.py       # Script to create GeoSpatial indexes
├── check_db.py           # Database verification script
├── requirements.txt      # Python dependencies (optional)
├── venv/                 # Virtual environment
└── README.md            # This file
```

## 🎨 Map Features

- **🔴 Red dot (small)**: Your selected apartment location
- **Colored dots (medium)**: Nearby restaurants, each with a unique color
- **Interactive legend**: Shows which color corresponds to which restaurant

## 🔧 Configuration

To change the MongoDB connection, edit `app.py`:

```python
client = MongoClient("mongodb://localhost:27017/")
db = client.geoloca  # Change database name here
```

## 📊 Sample Apartments

- Private Room in Bushwick
- Ribeira Charming Duplex
- Horto flat with small garden
- Apt Linda Vista Lagoa - Rio
- Modern Spacious 1 Bedroom Loft
- And more...

## 🤝 Contributing

Feel free to fork this project and submit pull requests for any improvements!

## 📝 License

This project is for educational purposes as part of a NoSQL course.

## 👨‍💻 Author

Created for a NoSQL Database course - 4th Year, Semester 7

---

**Note**: Make sure MongoDB is running before starting the application!
