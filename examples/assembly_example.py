import requests
import json
from typing import Dict, Any, List

class CATIAAssemblyClient:
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

    def create_product(self) -> Dict[str, Any]:
        """创建新的Product文档"""
        try:
            response = requests.post(
                f"{self.base_url}/api/catia/document",
                json={"operation": "create", "doc_type": "Product"},
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def add_component(self, file_path: str, position: List[float] = None) -> Dict[str, Any]:
        """添加组件"""
        if position is None:
            position = [0, 0, 0]
        try:
            response = requests.post(
                f"{self.base_url}/api/catia/assembly",
                json={
                    "operation": "add_component",
                    "file_path": file_path,
                    "position": position
                },
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_constraint(self, component1: str, component2: str, 
                         constraint_type: str, reference1: Any, reference2: Any) -> Dict[str, Any]:
        """创建约束"""
        try:
            response = requests.post(
                f"{self.base_url}/api/catia/assembly",
                json={
                    "operation": "create_constraint",
                    "component1": component1,
                    "component2": component2,
                    "constraint_type": constraint_type,
                    "reference1": reference1,
                    "reference2": reference2
                },
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def check_interference(self, body1: Any, body2: Any) -> Dict[str, Any]:
        """检查干涉"""
        try:
            response = requests.post(
                f"{self.base_url}/api/catia/analysis",
                json={
                    "operation": "interference",
                    "body1": body1,
                    "body2": body2
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
    client = CATIAAssemblyClient()

    # 连接到CATIA
    if not client.connect():
        print("连接CATIA失败")
        return

    # 创建新装配文档
    result = client.create_product()
    if result["status"] != "success":
        print(f"创建装配文档失败: {result['message']}")
        return

    # 添加第一个组件
    result = client.add_component("C:/temp/part1.CATPart", [0, 0, 0])
    if result["status"] != "success":
        print(f"添加第一个组件失败: {result['message']}")
        return

    # 添加第二个组件
    result = client.add_component("C:/temp/part2.CATPart", [100, 0, 0])
    if result["status"] != "success":
        print(f"添加第二个组件失败: {result['message']}")
        return

    # 创建约束
    result = client.create_constraint(
        "Part1",
        "Part2",
        "Coincidence",
        "Face1",
        "Face2"
    )
    if result["status"] != "success":
        print(f"创建约束失败: {result['message']}")
        return

    # 检查干涉
    result = client.check_interference("Body1", "Body2")
    if result["status"] != "success":
        print(f"检查干涉失败: {result['message']}")
        return
    else:
        interference = result["data"]["interference"]
        if interference:
            print("发现干涉！")
        else:
            print("没有干涉")

    # 保存文档
    result = client.save_document("C:/temp/assembly.CATProduct")
    if result["status"] != "success":
        print(f"保存文档失败: {result['message']}")
        return

    print("装配操作完成")

if __name__ == "__main__":
    main() 