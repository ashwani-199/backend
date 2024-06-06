from app import app
import os

if __name__ == '__main__':
    print('here')
    app.run(host=os.getenv('IP', '0.0.0.0'), 
            port=int(os.getenv('PORT', 5000)))
