# 🎨 GUI Usage Guide

## Hướng dẫn sử dụng GUI cho Hybrid P2P File Sharing

### 🖥️ Server GUI (`server_gui.py`)

#### Features:
- **Real-time monitoring** server hoạt động
- **Statistics dashboard** hiển thị số lượng clients, files, connections
- **Connected Clients tab** - Xem danh sách clients đang online
- **Shared Files tab** - Xem tất cả files trong network
- **Server Logs tab** - Monitor hoạt động của server

#### Cách sử dụng:

1. **Chạy Server GUI:**
```bash
python server_gui.py
```

2. **Start Server:**
   - Click nút "▶ START SERVER"
   - Server sẽ chạy trên `127.0.0.1:5000`
   - Status chuyển thành "● Running" màu xanh

3. **Monitor:**
   - Tab "👥 Connected Clients": Xem clients đang online
   - Tab "📁 Shared Files": Xem files được share
   - Tab "📋 Server Logs": Xem activity logs

4. **Stop Server:**
   - Click nút "⬛ STOP SERVER"

---

### 📁 Client GUI (`client_gui.py`)

#### Features:
- **Easy connection** với visual feedback
- **My Files tab** - Quản lý files trong repository
- **Network Files tab** - Discover và download files
- **Activity Logs tab** - Xem hoạt động của client
- **Search functionality** - Tìm kiếm files trên network

#### Cách sử dụng:

1. **Chạy Client GUI:**
```bash
python client_gui.py
```

Hoặc chạy nhiều clients (mở nhiều cửa sổ):
```bash
# Terminal 1
python client_gui.py

# Terminal 2 (client khác)
python client_gui.py

# Terminal 3 (client thứ 3)
python client_gui.py
```

2. **Connect to Server:**
   - Nhập **Client Name** (ví dụ: "Alice", "Bob", "Charlie")
   - Nhập **Port** (ví dụ: 5001, 5002, 5003 - mỗi client khác nhau)
   - Click "🔗 CONNECT"
   - Đợi status chuyển thành "● Connected" màu xanh

3. **Add Files:**
   - Vào tab "📂 My Files"
   - Click "➕ Add File"
   - Chọn file từ máy tính
   - File sẽ được copy vào repository

4. **Publish Files:**
   - Select file trong "My Files" list
   - Click "📤 Publish Selected"
   - File sẽ được đăng ký lên server index

5. **Discover Files:**
   - Vào tab "🌐 Network Files"
   - Click "🔍 Discover Files"
   - Danh sách files trên network sẽ hiển thị

6. **Download Files:**
   - Trong "Network Files" tab
   - Select file muốn download
   - Click "📥 Download Selected"
   - File sẽ được tải về qua P2P (trực tiếp từ peer, không qua server)

7. **Search Files:**
   - Dùng search box trong "Network Files" tab
   - Gõ tên file để filter

8. **View Logs:**
   - Vào tab "📋 Activity Logs"
   - Xem tất cả hoạt động (connect, publish, download...)

---

## 🎬 Demo Workflow

### Scenario: Alice share file, Bob download

**Step 1: Start Server**
```bash
python server_gui.py
```
- Click "▶ START SERVER"

**Step 2: Alice connects (Terminal 1)**
```bash
python client_gui.py
```
- Client Name: `Alice`
- Port: `5001`
- Click "🔗 CONNECT"

**Step 3: Alice adds & publishes file**
- Tab "📂 My Files"
- Click "➕ Add File"
- Chọn file (ví dụ: `report.pdf`)
- Select file vừa add
- Click "📤 Publish Selected"

**Step 4: Bob connects (Terminal 2)**
```bash
python client_gui.py
```
- Client Name: `Bob`
- Port: `5002`
- Click "🔗 CONNECT"

**Step 5: Bob discovers & downloads**
- Tab "🌐 Network Files"
- Click "🔍 Discover Files"
- Thấy `report.pdf` từ Alice
- Select `report.pdf`
- Click "📥 Download Selected"
- File tải về qua P2P!

**Step 6: Monitor on Server**
- Server GUI hiển thị:
  - 2 clients: Alice, Bob
  - 1 file: report.pdf
  - Providers: Alice (và Bob sau khi download xong)

---

## 🎨 UI Highlights

### Server GUI:
- ✅ **Dark theme** cho server monitoring
- ✅ **Color-coded stats**: Blue (clients), Purple (files), Teal (connections)
- ✅ **Real-time updates** mỗi giây
- ✅ **Professional dashboard** style

### Client GUI:
- ✅ **Clean, modern interface** với blue theme
- ✅ **Intuitive tabs**: My Files, Network Files, Logs
- ✅ **Visual feedback**: Colors cho status (green = connected, red = disconnected)
- ✅ **File size formatting**: Tự động convert B/KB/MB/GB
- ✅ **Search functionality** với real-time filter

---

## 💡 Tips

1. **Multiple Clients**: Mỗi client phải dùng **port khác nhau**
   - Client 1: Port 5001
   - Client 2: Port 5002
   - Client 3: Port 5003
   - ...

2. **Repository**: Mỗi client có repository riêng trong `./repository/<client_name>/`

3. **Auto-refresh**: My Files tự động refresh mỗi 5 giây

4. **Test files**: Dùng files trong `test_files/` folder để test

5. **Logs**: Xem logs tab để debug nếu có lỗi

---

## 🐛 Troubleshooting

### Client không connect được:
- ✅ Kiểm tra Server đã start chưa
- ✅ Kiểm tra port chưa bị dùng
- ✅ Xem logs tab để biết lỗi gì

### Download failed:
- ✅ Kiểm tra provider còn online không
- ✅ Refresh discover để update danh sách
- ✅ Kiểm tra firewall

### GUI không mở:
- ✅ Đảm bảo Python có Tkinter (built-in)
- ✅ Trên Linux có thể cần: `sudo apt-get install python3-tk`

---

## 📸 Screenshots Description

### Server GUI:
```
┌─────────────────────────────────────────────────┐
│     🖥️ P2P FILE SHARING SERVER                 │
│   Centralized Index Server - Hybrid P2P        │
├─────────────────────────────────────────────────┤
│ [▶ START] [⬛ STOP]  ● Running                  │
├─────────────────────────────────────────────────┤
│  👥 Clients │ 📁 Files │ 🔗 Connections        │
│      2      │    3     │       2               │
├─────────────────────────────────────────────────┤
│ [👥 Connected Clients] [📁 Shared Files] [...] │
│                                                 │
│  Hostname      │ Port │ Files │ Last Seen      │
│  Alice:5001    │ 5001 │   2   │ 10:30:45      │
│  Bob:5002      │ 5002 │   1   │ 10:31:12      │
└─────────────────────────────────────────────────┘
```

### Client GUI:
```
┌─────────────────────────────────────────────────┐
│        📁 P2P File Sharing Client              │
│    Share and download files from network       │
├─────────────────────────────────────────────────┤
│ Client Name: [Alice  ] Port: [5001] [🔗 CONNECT]│
│                                   ● Connected   │
├─────────────────────────────────────────────────┤
│ [📂 My Files] [🌐 Network Files] [📋 Logs]     │
│                                                 │
│ [➕ Add File] [📤 Publish] [🔄 Refresh]        │
│                                                 │
│  Filename        │ Size    │ Status            │
│  report.pdf      │ 1.2 MB  │ Local             │
│  notes.txt       │ 3.4 KB  │ Local             │
└─────────────────────────────────────────────────┘
```

---

## 🎓 For Presentation

Khi demo cho thầy:

1. **Mở Server GUI** - Giải thích chức năng monitoring
2. **Mở 2-3 Client GUIs** - Demo multiple clients
3. **Client 1**: Add file → Publish
4. **Server**: Show file xuất hiện trong index
5. **Client 2**: Discover → Download
6. **Server**: Show cả 2 clients đều có file
7. **Highlight**: P2P transfer (không qua server cho data)

**Điểm cộng UI:**
- ✅ Professional design
- ✅ Real-time monitoring
- ✅ User-friendly
- ✅ Visual feedback
- ✅ Error handling với messageboxes
- ✅ Color-coded status

Good luck! 🚀
