"""
吸菸監控系統 - 客戶端程式
支援多種攝影機來源:
1. USB 攝影機 (camera_type='usb', source=0)
2. RTSP 串流 (camera_type='rtsp', source='rtsp://...')
3. 本地攝影機 (camera_type='local', source=0)
"""

import cv2
import asyncio
import websockets
import json
import base64
import time
from pathlib import Path
import argparse

class CameraClient:
    def __init__(self, server_url: str, api_key: str, camera_source: str, camera_type: str = 'local'):
        """
        初始化攝影機客戶端
        
        Args:
            server_url: 伺服器 WebSocket URL (例如: ws://localhost:8000)
            api_key: 攝影機 API Key
            camera_source: 攝影機來源
                - USB/本地: "0", "1", "2" (攝影機編號)
                - RTSP: "rtsp://username:password@ip:port/stream"
                - HTTP: "http://ip:port/video"
            camera_type: 攝影機類型 ('local', 'usb', 'rtsp')
        """
        self.server_url = server_url
        self.api_key = api_key
        self.camera_source = camera_source
        self.camera_type = camera_type
        self.cap = None
        self.is_running = False
        
    def init_camera(self):
        """初始化攝影機"""
        try:
            if self.camera_type in ['local', 'usb']:
                # USB 或本地攝影機
                camera_id = int(self.camera_source)
                self.cap = cv2.VideoCapture(camera_id)
                
                # 設定解析度 (降低以減少頻寬)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
                self.cap.set(cv2.CAP_PROP_FPS, 15)
                
            elif self.camera_type == 'rtsp':
                # RTSP 串流 (例如小米監視器)
                self.cap = cv2.VideoCapture(self.camera_source)
                
                # RTSP 建議設定
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 減少延遲
            
            if not self.cap.isOpened():
                raise Exception("無法開啟攝影機")
            
            print(f"✅ 攝影機初始化成功 [{self.camera_type}]: {self.camera_source}")
            return True
            
        except Exception as e:
            print(f"❌ 攝影機初始化失敗: {e}")
            return False
    
    def read_frame(self):
        """讀取一幀影像"""
        if self.cap is None or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            print("⚠️ 讀取影像失敗")
            return None
        
        return frame
    
    def encode_frame(self, frame):
        """將影像編碼為 base64"""
        # 壓縮影像品質以減少頻寬
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
        _, buffer = cv2.imencode('.jpg', frame, encode_param)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        return frame_base64
    
    async def start_streaming(self):
        """開始串流到伺服器"""
        if not self.init_camera():
            return
        
        ws_url = f"{self.server_url}/ws/upload/{self.api_key}"
        print(f"🔄 正在連線到伺服器: {ws_url}")
        
        try:
            async with websockets.connect(ws_url) as websocket:
                print("✅ 已連線到伺服器")
                self.is_running = True
                
                frame_count = 0
                last_alert_time = 0
                
                while self.is_running:
                    # 讀取影像
                    frame = self.read_frame()
                    if frame is None:
                        await asyncio.sleep(0.1)
                        continue
                    
                    # 編碼影像
                    frame_base64 = self.encode_frame(frame)
                    
                    # 發送到伺服器
                    try:
                        await websocket.send(json.dumps({
                            "type": "frame",
                            "data": frame_base64
                        }))
                        
                        frame_count += 1
                        
                        # 接收伺服器回應
                        response = await asyncio.wait_for(
                            websocket.recv(),
                            timeout=1.0
                        )
                        
                        data = json.loads(response)
                        
                        # 處理警報
                        if data.get("type") == "alert":
                            current_time = time.time()
                            # 避免頻繁警報(每 5 秒最多一次)
                            if current_time - last_alert_time > 5:
                                print(f"🚨 警報！偵測到吸菸行為")
                                print(f"   信心度: {data['data'].get('max_confidence', 0):.2f}")
                                last_alert_time = current_time
                        
                        # 顯示狀態 (每 30 幀顯示一次)
                        if frame_count % 30 == 0:
                            print(f"📊 已上傳 {frame_count} 幀影像")
                    
                    except asyncio.TimeoutError:
                        print("⚠️ 伺服器回應超時")
                        continue
                    except Exception as e:
                        print(f"❌ 發送失敗: {e}")
                        break
                    
                    # 控制 FPS (約 15 FPS)
                    await asyncio.sleep(0.066)
        
        except websockets.exceptions.InvalidStatusCode as e:
            print(f"❌ 連線失敗: {e}")
            print("💡 請檢查:")
            print("   1. API Key 是否正確")
            print("   2. 伺服器是否正在運行")
            print("   3. 網路連線是否正常")
        
        except Exception as e:
            print(f"❌ 錯誤: {e}")
        
        finally:
            self.stop()
    
    def stop(self):
        """停止串流"""
        self.is_running = False
        if self.cap is not None:
            self.cap.release()
        print("⏹️ 攝影機已停止")


def main():
    """主程式"""
    parser = argparse.ArgumentParser(description='吸菸監控系統 - 攝影機客戶端')
    
    parser.add_argument(
        '--server',
        type=str,
        default='ws://localhost:8000',
        help='伺服器 WebSocket URL (預設: ws://localhost:8000)'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        required=True,
        help='攝影機 API Key (必填)'
    )
    
    parser.add_argument(
        '--source',
        type=str,
        default='0',
        help='攝影機來源 (預設: 0)\n'
             'USB攝影機: 0, 1, 2...\n'
             'RTSP: rtsp://username:password@ip:port/stream\n'
             '小米監視器: rtsp://admin:password@192.168.1.100:554/stream1'
    )
    
    parser.add_argument(
        '--type',
        type=str,
        choices=['local', 'usb', 'rtsp'],
        default='local',
        help='攝影機類型 (預設: local)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎥 吸菸監控系統 - 攝影機客戶端")
    print("=" * 60)
    print(f"伺服器: {args.server}")
    print(f"API Key: {args.api_key[:8]}...")
    print(f"攝影機類型: {args.type}")
    print(f"攝影機來源: {args.source}")
    print("=" * 60)
    
    # 建立客戶端
    client = CameraClient(
        server_url=args.server,
        api_key=args.api_key,
        camera_source=args.source,
        camera_type=args.type
    )
    
    # 開始串流
    try:
        asyncio.run(client.start_streaming())
    except KeyboardInterrupt:
        print("\n⏹️ 使用者中斷")
        client.stop()


if __name__ == "__main__":
    # 使用範例:
    # 
    # 1. USB 攝影機 (編號 0):
    #    python camera_client.py --api-key YOUR_API_KEY --type usb --source 0
    # 
    # 2. 小米監視器 (RTSP):
    #    python camera_client.py --api-key YOUR_API_KEY --type rtsp --source "rtsp://admin:password@192.168.1.100:554/stream1"
    # 
    # 3. 本地攝影機:
    #    python camera_client.py --api-key YOUR_API_KEY --type local --source 0
    
    main()
