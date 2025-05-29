```mermaid
flowchart TD
    A([Bắt đầu]) --> B[Khởi động Playwright codegen và WatchHandler]
    B --> C[/Thiết lập biến theo dõi file:<br/>- last_line_count = 0<br/>- last_content_hash = None/]
    
    C --> D[Bắt đầu theo dõi file JSONL tạm]
    
    subgraph PlaywrightAndWatcher["Playwright Test và WatchHandler"]
        E[Chạy test và tương tác với web] --> F[/Sinh và lưu flow JSONL vào file tạm/]
        F --> G{Phát hiện thay đổi file?}
        G -- Không --> E
        G -- Có --> H[/Kiểm tra hash nội dung/]
        H --> I{Hash thay đổi?}
        I -- Không --> E
        I -- Có --> J[/Đếm số dòng hiện tại/]
        
        J --> K{So sánh số dòng}
        K -- Dòng tăng lên --> L[/Đọc dòng mới thêm vào/]
        L --> M[Format dòng mới theo chuẩn JSONL]
        M --> N[/Thêm vào file JSONL đích/]
        
        K -- Số dòng không đổi --> O{Chỉ dòng cuối thay đổi?}
        O -- Có --> P[/Xóa dòng cuối của file đích/]
        P --> Q[Format lại dòng cuối]
        Q --> R[/Thêm dòng đã format vào file đích/]
        
        O -- Không --> S([Không làm gì])
        
        K -- Số dòng giảm --> T[/Ghi lại toàn bộ file đích/]
        
        N --> U[/Cập nhật biến theo dõi/]
        R --> U
        S --> U
        T --> U
        
        U --> V{Tiếp tục test?}
        V -- Có --> E
        V -- Không --> W([Kết thúc])
    end
    
    D --> PlaywrightAndWatcher
    W --> X([Kết thúc chương trình])
