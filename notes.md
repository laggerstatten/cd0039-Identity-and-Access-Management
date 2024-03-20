Gitbash::::


cd backend/src
python -m venv venv
/c/Users/darwi/AppData/Local/Programs/Python/Python37/python -m venv venv

source venv/Scripts/activate
pip install -r requirements.txt



cd backend/src
source venv/Scripts/activate
export FLASK_APP=api.py;
flask run --reload


cd frontend

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
nvm ls-remote
nvm install 14.17.0
npm install -g cordova
npm install -g ionic
npm install -g @angular/cli
npm install --save-dev @angular-devkit/build-angular
npm install --save-dev node-sass

cd frontend
ionic repair
ionic serve



Test Auth0

curl --request POST \
  --url https://dev-2bm0ojvr4sfeljpt.us.auth0.com/oauth/token \
  --header 'content-type: application/json' \
  --data '{"client_id":"UZPiVAp0j81CCJdT1baqxTlANKSivf9d","client_secret":"ObIhMedk_2TYPIC8TD83BllqMDcaTYeDI-efE3fytQgibI01dvP6UhZ93X1rzMX3","audience":"http://localhost:5000","grant_type":"client_credentials"}'