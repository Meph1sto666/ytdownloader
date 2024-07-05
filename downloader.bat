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
IF NOT EXIST .\lib\ffmpeg.exe (
	ECHO [31mFFMPEG IS MISSING[0m: please put ffmpeg.exe into .\lib\ffmpeg.exe
	PAUSE
	EXIT
)

CALL .\venv\Scripts\activate
pip install -r .\requirements.txt
python main.py
PAUSE