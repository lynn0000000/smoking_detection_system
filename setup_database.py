#!/usr/bin/env python3
"""
資料庫初始化腳本
功能:
1. 建立資料庫和表格
2. 建立測試管理員帳號
"""

import sys
from pathlib import Path

# 加入專案路徑
sys.path.insert(0, str(Path(__file__).parent))

from server.database import Base, engine, SessionLocal, User
from server.auth import get_password_hash
import pymysql
from server.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

def create_database():
    """建立資料庫"""
    try:
        # 連線到 MySQL (不指定資料庫)
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        cursor = connection.cursor()
        
        # 建立資料庫
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ 資料庫 '{DB_NAME}' 建立成功")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ 建立資料庫失敗: {e}")
        return False
    
    return True

def create_tables():
    """建立所有表格"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ 資料表建立成功")
        return True
    except Exception as e:
        print(f"❌ 建立資料表失敗: {e}")
        return False

def create_admin_user():
    """建立測試管理員帳號"""
    db = SessionLocal()
    
    try:
        # 檢查是否已存在 admin 用戶
        existing_user = db.query(User).filter(User.username == "admin").first()
        
        if existing_user:
            print("⚠️  管理員帳號已存在,跳過建立")
            return True
        
        # 建立管理員
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="系統管理員",
            is_admin=True,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print("✅ 測試管理員帳號建立成功")
        print("   用戶名: admin")
        print("   密碼: admin123")
        print("   ⚠️  正式環境請務必修改密碼！")
        
        return True
        
    except Exception as e:
        print(f"❌ 建立管理員失敗: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

def main():
    """主程式"""
    print("=" * 60)
    print("  🚭 吸菸監控系統 - 資料庫初始化")
    print("=" * 60)
    
    print(f"\n資料庫設定:")
    print(f"  Host: {DB_HOST}")
    print(f"  Port: {DB_PORT}")
    print(f"  User: {DB_USER}")
    print(f"  Database: {DB_NAME}")
    print()
    
    # 步驟 1: 建立資料庫
    print("步驟 1/3: 建立資料庫...")
    if not create_database():
        print("\n❌ 初始化失敗！")
        return
    
    # 步驟 2: 建立表格
    print("\n步驟 2/3: 建立資料表...")
    if not create_tables():
        print("\n❌ 初始化失敗！")
        return
    
    # 步驟 3: 建立測試用戶
    print("\n步驟 3/3: 建立測試管理員...")
    if not create_admin_user():
        print("\n❌ 初始化失敗！")
        return
    
    print("\n" + "=" * 60)
    print("  ✅ 資料庫初始化完成！")
    print("=" * 60)
    print("\n下一步:")
    print("  1. 啟動伺服器: python -m server.main")
    print("  2. 測試系統: python test_system.py")
    print("  3. 或直接使用測試帳號登入:")
    print("     用戶名: admin")
    print("     密碼: admin123")
    print()

if __name__ == "__main__":
    main()
