PROJECT_ASTAR - DEMO TIM DUONG BANG A*, BFS, UCS

1. Mo ta
- Project mo phong bai toan tim duong tren ban do luoi 2D co vat can.
- Ho tro 3 thuat toan: A*, BFS va UCS.
- Co 2 che do chay:
  + GUI bang Tkinter
  + CLI de kiem tra nhanh trong terminal

2. Cau truc thu muc
project_astar/
├── main.py
├── astar.py
├── bfs.py
├── ucs.py
├── map_utils.py
├── visualization.py
├── test_maps/
│   ├── map1.txt
│   ├── map2.txt
│   └── map3.txt
└── readme.txt

3. Dinh dang map
- S: vi tri bat dau
- G: vi tri dich
- 0: o trong, di duoc
- 1: vat can, khong di duoc

Vi du:
S 0 0 1
0 1 0 0
0 0 0 G

4. Cach chay GUI
- Yeu cau: Python 3.10+
- Vao thu muc project_astar va chay:
  python main.py

5. Cach chay CLI
- Chay A* voi map1:
  python main.py --cli --algo "A*" --map test_maps/map1.txt

- Chay BFS voi map2:
  python main.py --cli --algo BFS --map test_maps/map2.txt

- Chay UCS voi map3:
  python main.py --cli --algo UCS --map test_maps/map3.txt

6. Y nghia ket qua
- Found path: co tim duoc duong di hay khong
- Expanded nodes: so nut da mo rong
- Path cost: so buoc di tu S den G
- Runtime: thoi gian chay
- Path: danh sach toa do tren duong di

7. Goi y mo rong cho bao cao mon hoc
- Them che do tao map bang chuot
- So sanh thuc nghiem giua A*, BFS, UCS tren nhieu map
- Thu nghiem nhieu heuristic khac nhau cho A*
- Luu ket qua ra file CSV de ve bieu do
- Them cho phep di cheo va thay doi chi phi moi o
