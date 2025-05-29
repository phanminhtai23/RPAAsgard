```mermaid
flowchart TD
    A([Bắt đầu]) --> C[Thiết lập biến ban đầu: <br/> - last_line_count = 0 <br/> - last_content_hash = None]
    C --> D[Theo dõi file INPUT]
    D --> E{Phát hiện thay đổi file?}
    
    E -- Có --> F[/Đọc file INPUT và tính hash nội dung/]
    E -- Không --> D
    F --> G{Hash thay đổi?}
    G -- Không --> D
    G -- Có --> H[/Đếm số dòng hiện tại/]
    
    H --> I{So sánh số dòng}
    I -- Dòng tăng lên --> J[/Thêm dòng mới vào file/]
    J --> K[Format dòng mới và ghi vào file KQ]
    K --> L[/Cập nhật biến theo dõi/]
    L --> D
    
    I -- Số dòng không đổi --> M{Chỉ dòng cuối thay đổi?}
    M -- Có --> N[/Xóa dòng cuối của file KQ/]
    N --> O[Format lại dòng cuối và ghi vào KQ]
    O --> L
    
    M -- Không --> P([Không làm gì])
    P --> L
    
    I -- Số dòng giảm --> Q[/Ghi lại toàn bộ file KQ/]
    Q --> L
    
    D -- Dừng chương trình --> R([Kết thúc])