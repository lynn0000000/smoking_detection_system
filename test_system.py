#!/usr/bin/env python3
"""
快速測試腳本 - 測試系統各項功能
"""

import requests
import json
import time

# 設定
SERVER_URL = "http://localhost:8000"
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "test123456",
    "full_name": "測試用戶"
}

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_register():
    """測試用戶註冊"""
    print_section("1. 測試用戶註冊")
    
    response = requests.post(
        f"{SERVER_URL}/api/auth/register",
        json=TEST_USER
    )
    
    if response.status_code == 200:
        print("✅ 註冊成功")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        return True
    else:
        print(f"❌ 註冊失敗: {response.status_code}")
        print(response.text)
        return False

def test_login():
    """測試登入"""
    print_section("2. 測試用戶登入")
    
    response = requests.post(
        f"{SERVER_URL}/api/auth/login",
        json={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        print("✅ 登入成功")
        print(f"Token: {token[:20]}...")
        return token
    else:
        print(f"❌ 登入失敗: {response.status_code}")
        print(response.text)
        return None

def test_get_me(token):
    """測試取得用戶資訊"""
    print_section("3. 測試取得用戶資訊")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{SERVER_URL}/api/auth/me", headers=headers)
    
    if response.status_code == 200:
        print("✅ 取得用戶資訊成功")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        return True
    else:
        print(f"❌ 失敗: {response.status_code}")
        return False

def test_create_camera(token):
    """測試新增攝影機"""
    print_section("4. 測試新增攝影機")
    
    cameras = [
        {
            "camera_name": "測試USB攝影機",
            "camera_type": "usb",
            "camera_source": "0",
            "location": "測試地點 A"
        },
        {
            "camera_name": "測試RTSP攝影機",
            "camera_type": "rtsp",
            "camera_source": "rtsp://test:test@192.168.1.100:554/stream1",
            "location": "測試地點 B"
        }
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    api_keys = []
    
    for camera in cameras:
        response = requests.post(
            f"{SERVER_URL}/api/cameras",
            headers=headers,
            json=camera
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 新增攝影機成功: {camera['camera_name']}")
            print(f"   API Key: {data['api_key']}")
            api_keys.append(data['api_key'])
        else:
            print(f"❌ 新增失敗: {response.status_code}")
    
    return api_keys

def test_list_cameras(token):
    """測試列出攝影機"""
    print_section("5. 測試列出攝影機")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{SERVER_URL}/api/cameras", headers=headers)
    
    if response.status_code == 200:
        cameras = response.json()
        print(f"✅ 取得 {len(cameras)} 個攝影機")
        for cam in cameras:
            print(f"   - {cam['camera_name']} ({cam['camera_type']}) [ID: {cam['id']}]")
        return True
    else:
        print(f"❌ 失敗: {response.status_code}")
        return False

def test_get_statistics(token):
    """測試統計資料"""
    print_section("6. 測試統計資料")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{SERVER_URL}/api/statistics", headers=headers)
    
    if response.status_code == 200:
        print("✅ 取得統計資料成功")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        return True
    else:
        print(f"❌ 失敗: {response.status_code}")
        return False

def test_get_detections(token):
    """測試取得偵測記錄"""
    print_section("7. 測試取得偵測記錄")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{SERVER_URL}/api/detections?limit=5", headers=headers)
    
    if response.status_code == 200:
        detections = response.json()
        print(f"✅ 取得 {len(detections)} 筆偵測記錄")
        return True
    else:
        print(f"❌ 失敗: {response.status_code}")
        return False

def main():
    print("="*60)
    print("  🚭 吸菸監控系統 - 功能測試")
    print("="*60)
    print(f"伺服器: {SERVER_URL}")
    print("="*60)
    
    # 確認伺服器是否運行
    try:
        response = requests.get(SERVER_URL, timeout=5)
        if response.status_code != 200:
            print("❌ 伺服器未運行或無法連線")
            return
    except Exception as e:
        print(f"❌ 無法連線到伺服器: {e}")
        print("💡 請確認伺服器是否已啟動: python -m server.main")
        return
    
    print("✅ 伺服器運行中")
    time.sleep(1)
    
    # 執行測試
    test_register()
    time.sleep(1)
    
    token = test_login()
    if not token:
        print("❌ 無法繼續測試，登入失敗")
        return
    
    time.sleep(1)
    test_get_me(token)
    time.sleep(1)
    
    api_keys = test_create_camera(token)
    time.sleep(1)
    
    test_list_cameras(token)
    time.sleep(1)
    
    test_get_statistics(token)
    time.sleep(1)
    
    test_get_detections(token)
    
    # 顯示客戶端啟動指令
    if api_keys:
        print("\n" + "="*60)
        print("  📷 客戶端啟動指令")
        print("="*60)
        for i, api_key in enumerate(api_keys, 1):
            print(f"\n攝影機 {i}:")
            print(f"python client/camera_client.py \\")
            print(f"  --server ws://localhost:8000 \\")
            print(f"  --api-key {api_key} \\")
            print(f"  --type usb \\")
            print(f"  --source 0")
    
    print("\n" + "="*60)
    print("  ✅ 測試完成！")
    print("="*60)

if __name__ == "__main__":
    main()
