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

def process_json_line(json_line_str, current_url_param, dry_run_for_url_only=False): # Thêm tham số mới
    """
    Chuyển đổi một dòng JSON từ output_codegen.jsonl sang format mong muốn.
    Trả về một tuple: (dòng_json_đã_chuyển_đổi_hoặc_None, url_hiện_tại_mới)
    Nếu dry_run_for_url_only là True, dòng_json_đã_chuyển_đổi sẽ là None.
    """
    try:
        data = json.loads(json_line_str)
        action = data.get('name')
        updated_url = current_url_param 
        
        # Logic cập nhật URL phải được thực hiện ngay cả trong dry run
        if action == 'navigate':
            nav_url = data.get('url')
            if nav_url:
                updated_url = nav_url
        elif action == 'openPage':
            # Theo logic gốc, openPage không thay đổi updated_url dựa trên data['url'] của nó.
            # Nó chỉ trả về updated_url (là current_url_param) và không tạo output.
            # Nếu nó CẦN thay đổi updated_url, logic ở đây phải giống 'navigate'.
            # Giữ nguyên theo logic gốc được cung cấp:
            pass # updated_url không thay đổi bởi openPage dựa trên data của nó.

        if dry_run_for_url_only:
            return None, updated_url

        # --- Từ đây là logic cho normal run (không phải dry run) ---
        if action == 'openPage': # Vẫn bỏ qua openPage cho output
            return None, updated_url

        timestamp = datetime.utcnow().isoformat(timespec='seconds') + "Z"
        entry = {
            "timestamp": timestamp,
            "action": action,
            # URL trong entry là URL *trước khi* hành động này (nếu là navigate) thay đổi nó.
            # Tuy nhiên, nếu là navigate, entry['url'] sẽ được cập nhật thành updated_url (URL mới).
            "url": current_url_param, # URL ngữ cảnh hiện tại
        }

        if action == 'navigate':
            # nav_url đã được dùng để cập nhật updated_url ở trên
            entry['url'] = updated_url # navigate action ghi lại URL mới của nó
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

        # elif action == 'openPage': # Đã xử lý ở trên (không tạo output)
        #     pass

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
            entry['selector'] = selector
            entry['generated_code'] = f"await page.setInputFiles('{selector}', 'file');" 

        elif action == 'selectOption':
            selector = data.get('selector', '')
            entry['selector'] = selector
            entry['generated_code'] = f"await page.selectOption('{selector}', 'option');"
            
        else: 
            # Bỏ qua các hành động không xác định khác
            return None, updated_url # Trả về updated_url đã tính toán (có thể đã đổi bởi navigate)

        return json.dumps(entry, ensure_ascii=False), updated_url
    except json.JSONDecodeError:
        # print(f"⚠️ Cảnh báo: Không thể decode JSON: {json_line_str.strip()}")
        return None, current_url_param # Quan trọng: trả về URL gốc nếu lỗi
    except Exception as e:
        # print(f"Lỗi khi xử lý dòng: {json_line_str.strip()} - {e}")
        return None, current_url_param

class WatcherEventHandler(FileSystemEventHandler):
    def __init__(self, filename_to_watch, output_filename):
        self.filename_to_watch = os.path.abspath(filename_to_watch)
        self.output_filename = os.path.abspath(output_filename)
        
        self.last_input_line_count = 0
        self.last_processed_url = "" 
        self.last_input_content_hash = None 
        
        print(f"🔍 Khởi tạo handler cho: {self.filename_to_watch}")
        self._trigger_processing() 

    def _read_input_and_get_lines_and_hash(self):
        """Đọc file input, trả về danh sách các dòng hợp lệ, hash nội dung, và số dòng."""
        if not os.path.exists(self.filename_to_watch):
            return [], None, 0 
        try:
            with open(self.filename_to_watch, 'r', encoding='utf-8') as f_in:
                content = f_in.read()
                content_hash = hash(content) 
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                return lines, content_hash, len(lines)
        except Exception as e:
            print(f"Lỗi khi đọc file input {self.filename_to_watch}: {e}")
            return [], None, 0

    def on_created(self, event):
        if not event.is_directory and event.src_path == self.filename_to_watch:
            print(f"✨ File {self.filename_to_watch} vừa được tạo.")
            self.last_input_content_hash = None 
            self._trigger_processing()

    def on_modified(self, event):
        if not event.is_directory and event.src_path == self.filename_to_watch:
            self._trigger_processing()

    def _trigger_processing(self):
        current_input_lines, current_hash, current_line_count = self._read_input_and_get_lines_and_hash()

        if current_hash == self.last_input_content_hash and current_hash is not None:
            return
        
        if not current_input_lines: 
            try:
                with open(self.output_filename, 'w', encoding='utf-8') as f_out:
                    f_out.write("") 
                print(f"🗑️ File input rỗng. File output {self.output_filename} đã được làm rỗng.")
                self.last_input_line_count = 0
                self.last_processed_url = ""
                self.last_input_content_hash = current_hash 
            except Exception as e:
                print(f"Lỗi khi làm rỗng file output: {e}")
            return

        if self.last_input_content_hash is None or \
           current_line_count < self.last_input_line_count:
            print(f"📜 Đã phát hiện thay đổi nội dung file, tui không làm gì đâu, tự sửa đii.")
            # print(f"📜 Thay đổi lớn hoặc lần đầu: Xử lý lại toàn bộ ({current_line_count} dòng).")
            # self._perform_full_rewrite(current_input_lines, current_hash)
        
        elif current_line_count == self.last_input_line_count: 
            # Đây là trường hợp anh muốn xử lý đặc biệt nè!
            print(f"✍️ Số dòng input không đổi ({current_line_count}). Cập nhật dòng cuối output.")
            self._perform_selective_last_line_update(current_input_lines, current_hash)
            
        elif current_line_count > self.last_input_line_count: 
            num_new_lines = current_line_count - self.last_input_line_count
            lines_to_append_process = current_input_lines[-num_new_lines:]
            print(f"➕ Phát hiện {num_new_lines} dòng input mới, xử lý và append.")
            self._perform_append(lines_to_append_process, current_hash, current_line_count)
        
    def _perform_full_rewrite(self, input_lines_to_process, new_input_hash):
        new_output_data = []
        current_url_for_rewrite = "" 
        for line_str in input_lines_to_process:
            # Chạy bình thường, không dry_run
            converted_line, current_url_for_rewrite = process_json_line(line_str, current_url_for_rewrite, dry_run_for_url_only=False)
            if converted_line:
                new_output_data.append(converted_line)
        
        try:
            with open(self.output_filename, 'w', encoding='utf-8') as f_out: 
                for l_write in new_output_data:
                    f_out.write(l_write + '\n')
            print(f"✅ (Full Rewrite) Ghi đè {len(new_output_data)} dòng. URL cuối: '{current_url_for_rewrite}'")
            
            self.last_input_line_count = len(input_lines_to_process)
            self.last_processed_url = current_url_for_rewrite
            self.last_input_content_hash = new_input_hash
        except Exception as e:
            print(f"❌ Lỗi ghi đè (Full Rewrite): {e}")

    def _perform_append(self, new_input_lines_to_process, new_input_hash, total_current_lines_in_input):
        appended_output_data = []
        current_url_for_append = self.last_processed_url 
        
        for line_str in new_input_lines_to_process:
            # Chạy bình thường, không dry_run
            converted_line, current_url_for_append = process_json_line(line_str, current_url_for_append, dry_run_for_url_only=False)
            if converted_line:
                appended_output_data.append(converted_line)
        
        if appended_output_data:
            try:
                with open(self.output_filename, 'a', encoding='utf-8') as f_out: 
                    for l_write in appended_output_data:
                        f_out.write(l_write + '\n')
                print(f"✅ (Append) Nối {len(appended_output_data)} dòng. URL cuối: '{current_url_for_append}'")
            except Exception as e:
                print(f"❌ Lỗi nối file (Append): {e}")
                self.last_input_content_hash = None 
                return 
        else:
            print("ℹ️ (Append) Không có output mới để nối.")

        self.last_input_line_count = total_current_lines_in_input
        self.last_processed_url = current_url_for_append
        self.last_input_content_hash = new_input_hash

    def _perform_selective_last_line_update(self, current_input_lines, new_input_hash):
        """
        Xóa dòng cuối của file output (nếu có), 
        xử lý lại dòng cuối của input và nối vào.
        Các dòng output trước đó được giữ nguyên timestamp.
        """
        preserved_output_prefix_lines = []
        if os.path.exists(self.output_filename):
            try:
                with open(self.output_filename, 'r', encoding='utf-8') as f_out_read:
                    # Đọc tất cả các dòng output hiện tại
                    all_current_output_lines = [line.strip() for line in f_out_read.readlines() if line.strip()]
                if all_current_output_lines:
                    # Giữ lại tất cả TRỪ dòng cuối cùng
                    preserved_output_prefix_lines = all_current_output_lines[:-1]
            except Exception as e:
                print(f"Lỗi đọc file output để cập nhật dòng cuối: {e}. Sẽ fallback về full rewrite.")
                self._perform_full_rewrite(current_input_lines, new_input_hash)
                return
        
        # Tính toán URL context cần thiết để xử lý dòng cuối của input.
        # URL này là URL sau khi đã xử lý (dry run) tất cả các dòng input TRƯỚC dòng cuối.
        url_context_for_last_input = ""
        if len(current_input_lines) > 1: # Nếu có nhiều hơn 1 dòng input
            input_prefix_for_url_calc = current_input_lines[:-1]
            for line_str in input_prefix_for_url_calc:
                # Chạy dry_run để lấy URL context, không tạo output
                _, url_context_for_last_input = process_json_line(line_str, url_context_for_last_input, dry_run_for_url_only=True)
        
        # Xử lý dòng cuối cùng của input (normal run, không dry_run)
        last_input_line_to_process = current_input_lines[-1]
        newly_formatted_last_output_json, final_url_after_all = process_json_line(last_input_line_to_process, url_context_for_last_input, dry_run_for_url_only=False)

        # Chuẩn bị nội dung cuối cùng để ghi ra file output
        final_output_lines_to_write = list(preserved_output_prefix_lines) # Bắt đầu với các dòng cũ đã giữ lại
        if newly_formatted_last_output_json:
            final_output_lines_to_write.append(newly_formatted_last_output_json) # Thêm dòng cuối mới (đã xử lý)

        try:
            with open(self.output_filename, 'w', encoding='utf-8') as f_out_write: # Ghi đè với nội dung mới
                for l_write in final_output_lines_to_write:
                    f_out_write.write(l_write + '\n')
            print(f"✅ (Selective Update) Cập nhật dòng cuối thành công ({len(final_output_lines_to_write)} dòng trong output). URL cuối: '{final_url_after_all}'")

            # Cập nhật trạng thái
            self.last_input_line_count = len(current_input_lines)
            self.last_processed_url = final_url_after_all
            self.last_input_content_hash = new_input_hash
        except Exception as e:
            print(f"❌ Lỗi ghi file (Selective Update): {e}")
            self.last_input_content_hash = None # Để lần sau có thể full rewrite nếu cần


if __name__ == "__main__":
    abs_input_file_path = os.path.abspath(INPUT_FILE_PATH)
    abs_output_file_path = os.path.abspath(OUTPUT_FILE_PATH)
    
    directory_to_watch = os.path.dirname(abs_input_file_path)

    if not os.path.exists(directory_to_watch):
        os.makedirs(directory_to_watch, exist_ok=True)
        print(f"📁 Đã tạo thư mục giám sát: {directory_to_watch}")

    # Đảm bảo file input tồn tại để watchdog có thể theo dõi
    if not os.path.exists(abs_input_file_path):
        try:
            open(abs_input_file_path, 'a', encoding='utf-8').close()
            print(f"📝 File input rỗng {abs_input_file_path} đã được tạo (nếu chưa có).")
        except Exception as e:
            print(f"Lỗi khi cố gắng tạo file input rỗng: {e}")

    print(f"📺 Bắt đầu giám sát file '{abs_input_file_path}' trong thư mục '{directory_to_watch}'")
    print(f"📝 Output sẽ được ghi vào: '{abs_output_file_path}'")
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
