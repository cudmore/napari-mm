## Install Napari

### Linux/Debian/Ubuntu

```
sudo apt-get install python3-pyqt5
sudo apt-get install python3-pyqt5.qtopengl

# clone
git clone https://github.com/napari/napari.git

# virtual environment
python -m venv mm_env
source mm_env/bin/activate

# force particular version of PyQt (newer versions do not work)
pip install PyQt5==5.12.3

pip install -e napari/.[PyQt5]
```
