1. go to baseapp folder
    cd baseapp/
2. create a virtual environment on current folder
    virtualenv -p python3 .
3. active the virtual environment
    source bin/activate
4. install depencency
    pip install -r requirements.txt
5. upgrade python library
    pip install --upgrade -r requirements.txt

to run application:
    uvicorn baseapp.app:app --port 1899 --reload