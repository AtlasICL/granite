# Container block allocation program
Auhor: Emre Acarsoy

# Build

### Powershell:
```
mkdir block_allocator
cd block_allocator
python -m venv venv
./venv/Scripts/Activate.ps1
pip install -r requirements.txt
python main.py
```

### cmd: 
```
mkdir block_allocator
cd block_allocator
python -m venv venv
.\venv\Scripts\activate.bat
pip install -r requirements.txt
python main.py
```

- The blocks info must be in file `blocks.csv`, with headers for `BlockNo` and `Weight`.
- The container info is in `container_info.json`.

