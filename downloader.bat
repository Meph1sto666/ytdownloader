@ECHO OFF
IF NOT EXIST .\venv\ (
	IF EXIST .\lib\python310 (
		ECHO CREATING VENV FROM SHIPPED DEPENDENCY
		.\lib\python310\python.exe -m venv venv
	) ELSE (
		ECHO CREATING VENV FROM GLOBAL PYTHON
		python -m venv venv
	)
	ECHO VENV CREATED
)

CALL .\venv\Scripts\activate
pip install -r .\requirements.txt
python main.py
PAUSE