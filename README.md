git clone https://github.com/Transcribe.git

cd Transcribe

# Create a virtual environment
python -m venv venv

# Activate the virtual environment - Windows
.\venv\Scripts\activate

# Activate the virtual environment - Unix
source venv/bin/activate

pip install -r requirements.txt

#run the application with following command:
python src/app.py
