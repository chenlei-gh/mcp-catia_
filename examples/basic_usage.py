import requests
import json
from typing import Dict, Any

class CATIAClient:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.token = None
        self.headers = {}

    def connect(self) -> bool:
        """连接到CATIA服务"""
        try:
            response = requests.post(f"{self.base_url}/api/catia/connect")
            if response.status_code == 200:
                self.token = response.json().get("token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
                return True
            return False
        except Exception as e:
            print(f"连接失败: {str(e)}")
            return False

    def create_part(self) -> Dict[str, Any]:
        """创建新的Part文档"""
        try:
            response = requests.post(
                f"{self.base_url}/api/catia/document",
                json={"operation": "create", "doc_type": "Part"},
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_point(self, x: float, y: float, z: float) -> Dict[str, Any]:
        """创建点"""
        try:
            response = requests.post(
                f"{self.base_url}/api/catia/geometry",
                json={
                    "operation": "point",
                    "x": x,
                    "y": y,
                    "z": z
                },
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_line(self, start: list, end: list) -> Dict[str, Any]:
        """创建线"""
        try:
            response = requests.post(
                f"{self.base_url}/api/catia/geometry",
                json={
                    "operation": "line",
                    "start_point": start,
                    "end_point": end
                },
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_sketch(self, plane: Any) -> Dict[str, Any]:
        """创建草图"""
        try:
            response = requests.post(
                f"{self.base_url}/api/catia/sketch",
                json={
                    "operation": "create",
                    "plane": plane
                },
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_pad(self, sketch: Any, length: float) -> Dict[str, Any]:
        """创建凸台"""
        try:
            response = requests.post(
                f"{self.base_url}/api/catia/feature",
                json={
                    "operation": "pad",
                    "sketch": sketch,
                    "length": length
                },
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def save_document(self, file_path: str) -> Dict[str, Any]:
        """保存文档"""
        try:
            response = requests.post(
                f"{self.base_url}/api/catia/document",
                json={
                    "operation": "save",
                    "file_path": file_path
                },
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

def main():
    # 创建客户端实例
    client = CATIAClient()

    # 连接到CATIA
    if not client.connect():
        print("连接CATIA失败")
        return

    # 创建新文档
    result = client.create_part()
    if result["status"] != "success":
        print(f"创建文档失败: {result['message']}")
        return

    # 创建点
    result = client.create_point(0, 0, 0)
    if result["status"] != "success":
        print(f"创建点失败: {result['message']}")
        return

    # 创建线
    result = client.create_line([0, 0, 0], [100, 100, 0])
    if result["status"] != "success":
        print(f"创建线失败: {result['message']}")
        return

    # 创建草图
    result = client.create_sketch("XYPlane")
    if result["status"] != "success":
        print(f"创建草图失败: {result['message']}")
        return

    # 创建凸台
    result = client.create_pad("Sketch.1", 50.0)
    if result["status"] != "success":
        print(f"创建凸台失败: {result['message']}")
        return

    # 保存文档
    result = client.save_document("C:/temp/example.CATPart")
    if result["status"] != "success":
        print(f"保存文档失败: {result['message']}")
        return

    print("所有操作完成")

if __name__ == "__main__":
    main() 