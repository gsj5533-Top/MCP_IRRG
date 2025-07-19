import requests
import json
import time
from requests.exceptions import ConnectionError

def check_server_status(base_url: str, max_retries: int = 3, retry_delay: int = 2) -> bool:
    """检查服务器是否在运行
    
    Args:
        base_url (str): 服务器基础URL
        max_retries (int): 最大重试次数
        retry_delay (int): 重试间隔（秒）
    
    Returns:
        bool: 服务器是否可用
    """
    for i in range(max_retries):
        try:
            # 设置较短的超时时间，避免长时间等待
            response = requests.get(f"{base_url}/docs", timeout=5)
            
            if response.status_code == 200:
                print("服务器正在运行")
                return True
            else:
                print(f"服务器响应异常，状态码: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("服务器响应超时")
        except requests.exceptions.ConnectionError as e:
            if "Connection reset by peer" in str(e):
                print("服务器连接被重置，可能正在初始化...")
            else:
                print(f"连接错误: {e}")
        except Exception as e:
            print(f"检查服务器状态时出错: {e}")
            
        if i < max_retries - 1:
            print(f"等待 {retry_delay} 秒后重试...")
            time.sleep(retry_delay)
            
    return False

def test_irrigation_suggestion():
    """测试灌溉建议API"""
    
    base_url = "http://localhost:8000"
    
    # 检查服务器状态
    if not check_server_status(base_url):
        print("\n错误: 无法连接到服务器，请确保：")
        print("1. 服务器已经启动（运行 python server.py）")
        print("2. 服务器正在监听 8000 端口")
        print("3. 没有其他程序占用 8000 端口")
        return
    
    # 1. 测试有知识库的作物（花生）
    print("\n测试1: 查询花生的灌溉建议")
    try:
        # 设置较长的超时时间，因为第一次请求可能需要初始化向量数据库
        response = requests.post(
            "http://localhost:8000/api/irrigation/suggest",
            json={
                "city": "南京",
                "crop": "花生",
                "time_range": 7
            },
            timeout=30  # 30秒超时
        )
        
        # 检查响应状态
        if response.status_code == 200:
            print("请求成功")
            print(f"状态码: {response.status_code}")
            data = response.json()
            print(f"响应内容: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            # 检查知识库状态
            if data.get('status') == 'no_knowledge':
                print("\n警告: 未找到灌溉知识")
                print("请检查:")
                print("1. data/灌溉知识 目录是否包含正确的文档")
                print("2. 文档是否使用 UTF-8 编码")
                print("3. 向量数据库是否正确初始化")
        else:
            print(f"服务器返回错误状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
    except requests.exceptions.Timeout:
        print("请求超时，服务器可能正在初始化向量数据库，请稍后重试")
    except requests.exceptions.ConnectionError as e:
        print(f"连接错误: {e}")
        print("请确保服务器正在运行且没有崩溃")
    
    # 2. 测试未知作物（火龙果）
    print("\n测试2: 查询未知作物（火龙果）的灌溉建议")
    try:
        response = requests.post(
        "http://localhost:8000/api/irrigation/suggest",
        json={
            "city": "南京",
            "crop": "火龙果",
            "time_range": 7
        }
    )
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except ConnectionError as e:
        print(f"连接错误: {e}")
    except Exception as e:
        print(f"请求错误: {e}")

if __name__ == "__main__":
    try:
        test_irrigation_suggestion()
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
