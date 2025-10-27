# Hybrid P2P File Sharing Application

Ứng dụng chia sẻ file theo mô hình Hybrid Peer-to-Peer sử dụng TCP/IP protocol stack.

## 📋 Mô tả

Hệ thống kết hợp mô hình Client-Server và P2P:
- **Centralized Index Server**: Quản lý metadata (danh sách file và client)
- **Peer Clients**: Chia sẻ file trực tiếp với nhau (P2P), kết nối server để tìm kiếm

## 🏗️ Kiến trúc

```
┌─────────────────────────────────────────────────────────┐
│                   Index Server                          │
│  - Quản lý danh sách client                            │
│  - Lưu trữ metadata file                               │
│  - Không lưu file thực tế                              │
└─────────────────────────────────────────────────────────┘
                    ▲         ▲
                    │         │
        ┌───────────┘         └───────────┐
        │                                 │
┌───────▼────────┐               ┌───────▼────────┐
│   Client A     │◄─────P2P─────►│   Client B     │
│  - Repository  │               │  - Repository  │
│  - Peer Server │               │  - Peer Server │
└────────────────┘               └────────────────┘
```

## 📁 Cấu trúc Project

```
BTL1/
├── config.py              # Cấu hình (host, port, buffer size, ...)
├── protocol.py            # Định nghĩa protocol và message format
├── server/
│   ├── __init__.py
│   ├── server.py          # Server chính
│   └── index_manager.py   # Quản lý index/metadata
├── client/
│   ├── __init__.py
│   ├── client.py          # Client chính
│   ├── peer_server.py     # P2P server (nhận request từ peer)
│   └── file_manager.py    # Quản lý local repository
├── utils/
│   └── __init__.py        # Logging utilities
├── run_server.py          # Script chạy server (CLI)
├── run_client.py          # Script chạy client (CLI)
├── server_gui.py          # 🎨 Server GUI (Tkinter)
├── client_gui.py          # 🎨 Client GUI (Tkinter)
├── test_demo.py           # Automated test script
├── create_test_files.py   # Tạo test files
├── README.md              # Tài liệu chính
└── GUI_GUIDE.md           # 🎨 Hướng dẫn sử dụng GUI
```

## 🚀 Cài đặt và Chạy

### Yêu cầu

- Python 3.7+
- Không cần thư viện bên ngoài (chỉ dùng standard library)
- Tkinter (built-in với Python) - cho GUI version

### 🎨 Quick Start với GUI (Recommended)

#### Chạy Server GUI:
```bash
python server_gui.py
```
- Click "▶ START SERVER"
- Monitor clients và files real-time

#### Chạy Client GUI:
```bash
# Client 1
python client_gui.py

# Client 2 (mở terminal mới)
python client_gui.py
```
- Nhập tên và port khác nhau cho mỗi client
- Click "🔗 CONNECT"
- Add files, publish, discover, download với giao diện đẹp!

📖 **Chi tiết:** Xem [GUI_GUIDE.md](GUI_GUIDE.md)

---

### 📟 Command Line Version

### 1. Chạy Server

Mở terminal/cmd và chạy:

```bash
python run_server.py
```

Server sẽ chạy trên `127.0.0.1:5000` (có thể thay đổi trong `config.py`)

### 2. Chạy Client

Mở terminal/cmd khác và chạy:

```bash
# Client với port tự động
python run_client.py

# Client với port chỉ định
python run_client.py 5001

# Client với port và hostname
python run_client.py 5001 ClientA

# Client đầy đủ tham số
python run_client.py 5001 ClientA ./my_repo
```

**Tham số:**
- `port`: Port để client lắng nghe kết nối P2P (mặc định: auto)
- `hostname`: Tên client (mặc định: tự sinh)
- `repo_path`: Đường dẫn repository (mặc định: `./repository/<hostname>`)

### 3. Chạy nhiều Client

Để test P2P, mở nhiều terminal và chạy nhiều client với port khác nhau:

```bash
# Terminal 1
python run_client.py 5001 ClientA

# Terminal 2
python run_client.py 5002 ClientB

# Terminal 3
python run_client.py 5003 ClientC
```

## 📝 Hướng dẫn sử dụng

### Commands

Khi client đã chạy, bạn có thể dùng các lệnh sau:

#### 1. `add <path> [fname]`
Thêm file từ hệ thống vào repository

```bash
ClientA> add C:\Users\test.txt
ClientA> add C:\Data\report.pdf report.pdf
```

#### 2. `publish <lname> [fname]`
Publish file lên network (đăng ký với server)

```bash
ClientA> publish test.txt
ClientA> publish report.pdf my_report.pdf
```

#### 3. `discover`
Xem tất cả file trong network

```bash
ClientA> discover
📁 Files in network:
  • test.txt
    Providers: ClientA_5001
  • report.pdf
    Providers: ClientA_5001, ClientB_5002
```

#### 4. `fetch <fname>`
Tải file từ peer khác

```bash
ClientB> fetch test.txt
```

Workflow:
1. Client gửi FETCH đến server
2. Server trả về danh sách provider
3. Client kết nối trực tiếp đến peer (P2P)
4. Peer gửi file qua TCP stream
5. File được lưu vào repository

#### 5. `list`
Liệt kê file trong repository local

```bash
ClientA> list
📂 Local files:
  • test.txt (1,234 bytes)
  • report.pdf (56,789 bytes)
```

#### 6. `ping`
Kiểm tra kết nối với server

```bash
ClientA> ping
✓ Server is alive
```

#### 7. `quit` hoặc `exit`
Thoát client

```bash
ClientA> quit
```

## 🔧 Protocol Specification

### Control Channel (Client ↔ Server)

#### HELLO
```
Client → Server: HELLO <hostname> <port>
Server → Client: OK registered
```

#### PUBLISH
```
Client → Server: PUBLISH <fname> <hostname>
Server → Client: OK published
```

#### UPDATE
```
Client → Server: UPDATE <hostname> <file1> <file2> ...
Server → Client: OK synchronized
```

#### FETCH
```
Client → Server: FETCH <fname>
Server → Client: RESULT <hostname1> <hostname2> ...
```

#### PING/ALIVE
```
Client → Server: PING <hostname>
Server → Client: ALIVE
```

#### DISCOVER
```
Client → Server: DISCOVER
Server → Client: RESULT
                 <fname1>: <provider1>, <provider2>
                 <fname2>: <provider3>
```

### Data Channel (Client ↔ Client / P2P)

#### GET + DATA
```
Client A → Client B: GET <fname> <hostname>
Client B → Client A: DATA <fname> <size>
                     [binary data stream]
```

### Error Responses
```
ERROR <code> <description>

Ví dụ:
ERROR NOT_FOUND File not found
ERROR INVALID Invalid message format
```

## 📊 Workflow Examples

### Example 1: File Publishing

```
ClientA                    Server                    ClientB
   │                          │                         │
   │─────HELLO A 5001────────►│                         │
   │◄────OK registered────────│                         │
   │                          │                         │
   │──PUBLISH report.pdf A───►│                         │
   │◄────OK published─────────│                         │
```

### Example 2: File Fetching (P2P Transfer)

```
ClientB                    Server                    ClientA
   │                          │                         │
   │────FETCH report.pdf─────►│                         │
   │◄───RESULT A──────────────│                         │
   │                          │                         │
   │─────────GET report.pdf A────────────────────────►  │
   │◄────────DATA report.pdf 10240───────────────────   │
   │◄────────[binary stream]──────────────────────────  │
   │                          │                         │
   │──UPDATE B report.pdf────►│                         │
   │◄────OK synchronized──────│                         │
```

## 🧪 Test Scenarios

### Scenario 1: Basic File Sharing

1. Chạy server
2. Chạy Client A (port 5001)
3. Client A: `add test.txt` (tạo file test trước)
4. Client A: `publish test.txt`
5. Chạy Client B (port 5002)
6. Client B: `discover` (phải thấy test.txt từ ClientA)
7. Client B: `fetch test.txt`
8. Client B: `list` (phải thấy test.txt đã tải về)

### Scenario 2: Multiple Providers

1. Client A publish file1.txt
2. Client B fetch file1.txt (giờ cả A và B đều có)
3. Client C discover (phải thấy 2 providers: A, B)
4. Client C fetch file1.txt (có thể lấy từ A hoặc B)

### Scenario 3: Liveness Monitoring

1. Client A connect
2. Server tự động ping every 60s
3. Client A offline → sau 5 phút server cleanup
4. File của A bị remove khỏi index

## ⚙️ Configuration

File `config.py` có các tùy chọn:

```python
# Server
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000

# Client
CLIENT_HOST = '0.0.0.0'
DEFAULT_CLIENT_PORT_RANGE = (5001, 6000)

# Protocol
BUFFER_SIZE = 4096
CHUNK_SIZE = 10240  # File transfer chunk size

# Timeouts
CONNECTION_TIMEOUT = 30
PING_INTERVAL = 60  # Ping server every 60s

# Repository
DEFAULT_REPO_PATH = './repository'
```

## 📌 Features Implemented

### Core Requirements ✅

- ✅ Centralized Index Server
- ✅ Client registration (HELLO)
- ✅ File publishing (PUBLISH)
- ✅ File list synchronization (UPDATE)
- ✅ File lookup (FETCH)
- ✅ Peer-to-peer file transfer (GET/DATA)
- ✅ Network discovery (DISCOVER)
- ✅ Liveness monitoring (PING/ALIVE)
- ✅ Multi-threaded architecture
- ✅ Error handling and logging

### Server Functions ✅

- ✅ `accept_client()` - Nhận kết nối từ client
- ✅ `register_file()` - Đăng ký file vào index
- ✅ `sync_repo()` - Đồng bộ file list (UPDATE)
- ✅ `lookup_providers()` - Tìm provider có file
- ✅ `liveness_check()` - PING/ALIVE monitoring
- ✅ `deregister_client()` - Xóa client offline

### Client Functions ✅

- ✅ `connect_to_server()` - Kết nối và register với server
- ✅ `publish()` - Chia sẻ file (PUBLISH lname fname)
- ✅ `fetch()` - Tải file từ peer (FETCH fname)
- ✅ `update_file_list()` - Cập nhật danh sách file
- ✅ `receive_request()` - Nhận request từ peer (background thread)

## 🛠️ Troubleshooting

### Lỗi "Address already in use"

```bash
# Windows: Kill process trên port
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Hoặc đổi port trong config.py
```

### Client không connect được server

- Kiểm tra server đã chạy chưa
- Kiểm tra firewall
- Xem config SERVER_HOST, SERVER_PORT

### File transfer failed

- Kiểm tra file tồn tại: `list`
- Kiểm tra provider online: `discover`
- Xem log để debug

## 📚 Technical Details

### Threading Model

- **Server**: Mỗi client connection = 1 thread
- **Client**: 
  - Main thread: Interactive shell
  - Ping thread: Background ping server
  - Peer server thread: Chấp nhận P2P connections
  - Request handler threads: Xử lý từng peer request

### Data Transfer

- File được gửi qua TCP stream
- Chunk size: 10KB (configurable)
- Header format: `DATA <fname> <size>`
- Binary stream follows header

### Error Handling

- Network errors: Reconnect logic
- File not found: Error response to peer
- Invalid commands: ERROR message
- Client cleanup: Auto-remove sau timeout

## 👥 Authors

Bài tập lớn môn Mạng Máy Tính - HK251 (2023-2024)

## 📄 License

Educational purpose only
