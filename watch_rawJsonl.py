# live_converter.py
import json
from datetime import datetime
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Đường dẫn file input và output
INPUT_FILE_PATH = 'output_codegen.jsonl'
OUTPUT_FILE_PATH = 'converted.jsonl' # Giữ tên file output như script gốc của anh

def process_json_line(json_line_str, current_url_param):
    """
    Chuyển đổi một dòng JSON từ output_codegen.jsonl sang format mong muốn.
    Trả về một tuple: (dòng_json_đã_chuyển_đổi_hoặc_None, url_hiện_tại_mới)
    """
    try:
        data = json.loads(json_line_str)
        timestamp = datetime.utcnow().isoformat(timespec='seconds') + "Z"
        action = data.get('name')
        
        updated_url = current_url_param 
        
        entry = {
            "timestamp": timestamp,
            "action": action,
            "url": updated_url, 
        }

        if action == 'navigate':
            nav_url = data.get('url')
            if nav_url: # Chỉ cập nhật nếu URL thực sự có trong data
                updated_url = nav_url
            entry['url'] = updated_url
            entry['generated_code'] = f"await page.goto('{updated_url}');"
        
        elif action == 'click':
            selector = data.get('selector', '')
            entry['selector'] = selector
            entry['generated_code'] = f"await page.click('{selector}');"

        elif action == 'fill':
            selector = data.get('selector', '')
            text = data.get('text', '')
            entry['selector'] = selector
            entry['value'] = text
            entry['generated_code'] = f"await page.fill('{selector}', '{text}');"

        elif action == 'press':
            selector = data.get('selector', '')
            key = data.get('key', '')
            entry['selector'] = selector
            entry['key'] = key
            entry['generated_code'] = f"await page.press('{selector}', '{key}');"

        elif action == 'openPage':
            # Bỏ qua openPage như script gốc của anh
            return None, updated_url

        elif action == 'check':
            selector = data.get('selector', '')
            entry['selector'] = selector
            entry['generated_code'] = f"await page.check('{selector}');"

        elif action == 'uncheck':
            selector = data.get('selector', '')
            entry['selector'] = selector
            entry['generated_code'] = f"await page.uncheck('{selector}');"

        elif action == 'hover':
            selector = data.get('selector', '')
            entry['selector'] = selector
            entry['generated_code'] = f"await page.hover('{selector}');"

        elif action == 'focus':
            selector = data.get('selector', '')
            entry['selector'] = selector
            entry['generated_code'] = f"await page.focus('{selector}');"

        elif action == 'setInputFiles':
            selector = data.get('selector', '')
            # Giữ nguyên logic file placeholder như script gốc
            entry['selector'] = selector
            entry['generated_code'] = f"await page.setInputFiles('{selector}', 'file');" 

        elif action == 'selectOption':
            selector = data.get('selector', '')
            # Giữ nguyên logic option placeholder như script gốc
            entry['selector'] = selector
            entry['generated_code'] = f"await page.selectOption('{selector}', 'option');"
            
        else: 
            # Bỏ qua các hành động không xác định khác
            return None, updated_url

        return json.dumps(entry, ensure_ascii=False), updated_url
    except json.JSONDecodeError:
        print(f"⚠️ Cảnh báo: Không thể decode JSON: {json_line_str.strip()}")
        return None, current_url_param
    except Exception as e:
        print(f"Lỗi khi xử lý dòng: {json_line_str.strip()} - {e}")
        return None, current_url_param

class WatcherEventHandler(FileSystemEventHandler):
    def __init__(self, filename_to_watch, output_filename):
        self.filename_to_watch = os.path.abspath(filename_to_watch)
        self.output_filename = os.path.abspath(output_filename)
        self.current_url = ""
        self.last_processed_position = 0
        
        print(f"🔍 Khởi tạo handler cho: {self.filename_to_watch}")
        self._process_initial_content()

    def _process_initial_content(self):
        """Xử lý nội dung đã có sẵn trong file input khi khởi động."""
        try:
            if not os.path.exists(self.filename_to_watch):
                print(f"📄 File input {self.filename_to_watch} chưa tồn tại. Sẽ xử lý khi được tạo.")
                self.last_processed_position = 0
                return

            file_size = os.path.getsize(self.filename_to_watch)
            if file_size > 0:
                print(f"🔄 Đang xử lý nội dung có sẵn của {self.filename_to_watch} ({file_size} bytes)")
                with open(self.filename_to_watch, 'r', encoding='utf-8') as f_in:
                    lines = f_in.readlines() 
                    self.last_processed_position = f_in.tell()
                
                lines_to_write_to_output = []
                for line_str in lines:
                    stripped_line = line_str.strip()
                    if not stripped_line: continue
                    converted_line, new_url = process_json_line(stripped_line, self.current_url)
                    self.current_url = new_url
                    if converted_line:
                        lines_to_write_to_output.append(converted_line + '\n')
                
                if lines_to_write_to_output:
                    with open(self.output_filename, 'a', encoding='utf-8') as f_out:
                        for l_write in lines_to_write_to_output:
                            f_out.write(l_write)
                    print(f"✅ Xử lý ban đầu: Đã thêm {len(lines_to_write_to_output)} dòng. URL hiện tại: '{self.current_url}'")
            else: # File tồn tại nhưng rỗng
                self.last_processed_position = 0
                print(f"📄 File input {self.filename_to_watch} rỗng.")

        except Exception as e:
            print(f"❌ Lỗi khi xử lý nội dung ban đầu: {e}")
            self.last_processed_position = 0 

    def on_created(self, event):
        if not event.is_directory and event.src_path == self.filename_to_watch:
            print(f"✨ File {self.filename_to_watch} vừa được tạo.")
            self.last_processed_position = 0 
            self._process_new_content_from_file()

    def on_modified(self, event):
        if not event.is_directory and event.src_path == self.filename_to_watch:
            print(f"📝 File {self.filename_to_watch} có thay đổi.")
            self._process_new_content_from_file()

    def _process_new_content_from_file(self):
        try:
            # Đảm bảo file tồn tại trước khi lấy size
            if not os.path.exists(self.filename_to_watch):
                print(f"⚠️ File {self.filename_to_watch} không tìm thấy khi đang xử lý thay đổi.")
                return

            current_file_size = os.path.getsize(self.filename_to_watch)
            
            if current_file_size < self.last_processed_position:
                print(f"⚠️ File {self.filename_to_watch} bị thu nhỏ kích thước. Reset vị trí đọc về đầu file.")
                self.last_processed_position = 0
                self.current_url = "" # Trạng thái URL có thể không còn đúng
                # Cân nhắc xóa file output hoặc tạo backup nếu cần xử lý trường hợp này kỹ hơn

            if current_file_size <= self.last_processed_position and current_file_size > 0 : # Size không đổi hoặc chỉ có event mà không có content mới
                 # Vẫn có thể có trường hợp file được write mà size không đổi (overwrite cùng độ dài)
                 # nhưng readlines sẽ không trả về gì nếu con trỏ đã ở cuối.
                 # Đọc thử để chắc chắn.
                 pass


            with open(self.filename_to_watch, 'r', encoding='utf-8') as f_in:
                f_in.seek(self.last_processed_position)
                new_data_block = f_in.read() 
                new_read_position = f_in.tell()

            if not new_data_block.strip(): # Không có nội dung mới thực sự (chỉ có thể là whitespace)
                self.last_processed_position = new_read_position # Cập nhật vị trí dù không có gì
                return

            actual_new_lines = new_data_block.strip().split('\n')
            print(f"📥 Phát hiện {len(actual_new_lines)} dòng text mới.")
            
            lines_to_write_to_output = []
            for line_str in actual_new_lines:
                stripped_line = line_str.strip()
                if not stripped_line: continue
                
                converted_line, new_url = process_json_line(stripped_line, self.current_url)
                self.current_url = new_url 
                
                if converted_line:
                    lines_to_write_to_output.append(converted_line + '\n')
            
            if lines_to_write_to_output:
                with open(self.output_filename, 'a', encoding='utf-8') as f_out:
                    for l in lines_to_write_to_output:
                        f_out.write(l)
                print(f"✅ Đã xử lý và thêm {len(lines_to_write_to_output)} dòng. URL hiện tại: '{self.current_url}'")

            self.last_processed_position = new_read_position

        except FileNotFoundError:
            print(f"❌ Lỗi: File input {self.filename_to_watch} không tìm thấy khi đang xử lý.")
        except Exception as e:
            print(f"❌ Lỗi xảy ra khi xử lý nội dung mới: {e}")


if __name__ == "__main__":
    abs_input_file_path = os.path.abspath(INPUT_FILE_PATH)
    abs_output_file_path = os.path.abspath(OUTPUT_FILE_PATH)
    
    directory_to_watch = os.path.dirname(abs_input_file_path)

    if not os.path.exists(directory_to_watch):
        os.makedirs(directory_to_watch, exist_ok=True)
        print(f"📁 Đã tạo thư mục giám sát: {directory_to_watch}")
    
    print(f"📺 Bắt đầu giám sát file '{abs_input_file_path}' trong thư mục '{directory_to_watch}'")
    print(f"📝 Output sẽ được ghi vào (append): '{abs_output_file_path}'")
    print("Nhấn Ctrl+C để dừng chương trình.")

    event_handler = WatcherEventHandler(filename_to_watch=abs_input_file_path, 
                                        output_filename=abs_output_file_path)
    
    observer = Observer()
    observer.schedule(event_handler, directory_to_watch, recursive=False) 
    observer.start()
    
    try:
        while True:
            time.sleep(1) # Giữ chương trình chạy
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Chương trình giám sát đã dừng bởi người dùng.")
    observer.join()
