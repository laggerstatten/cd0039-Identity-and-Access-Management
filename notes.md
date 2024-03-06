Gitbash::::


cd backend/src
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt



cd backend/src
source venv/Scripts/activate
export FLASK_APP=api.py;
flask run --reload


cd frontend

npm install
ionic serve