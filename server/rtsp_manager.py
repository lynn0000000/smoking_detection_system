import subprocess
import sys
import os
import time
from typing import Dict, Optional

class RTSPClientManager:
    def __init__(self):
        self.clients: Dict[int, dict] = {}
    
    def start(self, camera_id: int, api_key: str, rtsp_url: str) -> dict:
        """啟動 RTSP 攝影機客戶端"""
        if camera_id in self.clients:
            old_process = self.clients[camera_id]["process"]
            if old_process.poll() is not None:
                # 舊進程已結束，清理
                try:
                    self.clients[camera_id]["log_file"].close()
                except:
                    pass
                del self.clients[camera_id]
            else:
                return {
                    "success": False,
                    "message": "客戶端已在執行中",
                    "status": "running"
                }


        
        try:
            # 建立 logs 目錄
            os.makedirs("logs", exist_ok=True)
            log_path = f"logs/camera_{camera_id}.log"
            
            # 取得專案根目錄
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # camera_client.py 路徑
            client_script = os.path.join(project_root, 'client', 'camera_client.py')
            
            # 檢查檔案是否存在
            if not os.path.exists(client_script):
                print(f"❌ 找不到 camera_client.py: {client_script}")
                return {
                    "success": False,
                    "message": f"找不到 camera_client.py: {client_script}",
                    "status": "error"
                }
            
            # 建立指令（修正參數名稱）
            cmd = [
                sys.executable,
                client_script,
                '--server', 'ws://localhost:8000',
                '--api-key', api_key,
                '--type', 'rtsp',      # ✅ 正確的參數
                '--source', rtsp_url   # ✅ 正確的參數
            ]
            
            print(f"啟動 RTSP 客戶端 [Camera {camera_id}]")
            print(f"指令: {' '.join(cmd)}")
            print(f"日誌: {log_path}")
            
            # 啟動子進程
            log_file = open(log_path, 'w', encoding='utf-8', errors='replace')  # ✅ 加 errors='replace'
            process = subprocess.Popen(
                cmd,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            # 等待一下確認進程啟動
            time.sleep(1)
            
            # 檢查進程是否還在執行
            if process.poll() is not None:
                log_file.close()
                
                # 🔥 修正：讀取日誌時處理編碼錯誤
                error_log = ""
                for encoding in ['utf-8', 'cp950', 'gbk', 'latin-1']:
                    try:
                        with open(log_path, 'r', encoding=encoding, errors='ignore') as f:
                            error_log = f.read()
                        break
                    except:
                        continue
                
                if not error_log:
                    error_log = "無法讀取日誌檔案"
                
                print(f"camera_client.py 啟動失敗:")
                print(error_log)
                return {
                    "success": False,
                    "message": "camera_client.py 啟動後立即結束",
                    "error": error_log,
                    "status": "crashed"
                }
            
            # 儲存進程資訊
            self.clients[camera_id] = {
                "process": process,
                "log_file": log_file,
                "api_key": api_key,
                "rtsp_url": rtsp_url,
                "start_time": time.time()
            }
            
            print(f"RTSP 客戶端已啟動 [Camera {camera_id}] PID: {process.pid}")
            
            return {
                "success": True,
                "message": "RTSP 客戶端已啟動",
                "status": "started",
                "pid": process.pid
            }
            
        except Exception as e:
            print(f"啟動 RTSP 客戶端失敗: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": str(e),
                "status": "error"
            }
    
    def stop(self, camera_id: int) -> dict:
        """停止 RTSP 攝影機客戶端"""
        if camera_id not in self.clients:
            return {
                "success": False,
                "message": "客戶端未在執行",
                "status": "not_running"
            }
        
        try:
            client_info = self.clients[camera_id]
            process = client_info["process"]
            log_file = client_info["log_file"]
            
            # 終止進程
            process.terminate()
            
            # 等待進程結束
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            
            # 關閉日誌檔案
            try:
                log_file.close()
            except:
                pass
            
            # 移除客戶端資訊
            del self.clients[camera_id]
            
            print(f"RTSP 客戶端已停止 [Camera {camera_id}]")
            
            return {
                "success": True,
                "message": "RTSP 客戶端已停止",
                "status": "stopped"
            }
            
        except Exception as e:
            print(f"停止 RTSP 客戶端失敗: {e}")
            return {
                "success": False,
                "message": str(e),
                "status": "error"
            }
    
    def get_status(self, camera_id: int) -> dict:
        """取得 RTSP 攝影機客戶端狀態"""
        if camera_id not in self.clients:
            return {
                "running": False,
                "status": "not_running"
            }
        
        client_info = self.clients[camera_id]
        process = client_info["process"]
        
        # 檢查進程是否還在執行
        if process.poll() is not None:
            # 進程已結束
            try:
                client_info["log_file"].close()
            except:
                pass
            del self.clients[camera_id]
            return {
                "running": False,
                "status": "crashed"
            }
        
        return {
            "running": True,
            "status": "running",
            "pid": process.pid,
            "uptime": time.time() - client_info["start_time"]
        }
    
    def stop_all(self):
        """停止所有 RTSP 攝影機客戶端"""
        camera_ids = list(self.clients.keys())
        for camera_id in camera_ids:
            self.stop(camera_id)
        print("已停止所有 RTSP 客戶端")

# 建立全域實例
rtsp_manager = RTSPClientManager()