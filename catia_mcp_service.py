from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required
import pycatia
import os
from dotenv import load_dotenv
from datetime import timedelta
import logging
from typing import Dict, List, Any, Optional, Union
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('catia_mcp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)
api = Api(app)

# JWT配置
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

class CATIAService:
    def __init__(self):
        self.catia = None
        self.documents = None
        self.part_document = None
        self.part = None
        self.hybrid_bodies = None
        self.parameters = None
        self.sketches = None
        self.bodies = None
        self.measure = None
        self.analysis = None
        self.drawing = None
        self.product = None
        self.system = None
        
    def connect(self):
        try:
            self.catia = pycatia.catia_application()
            self.documents = self.catia.documents
            self.system = self.catia.system
            return True
        except Exception as e:
            logger.error(f"连接CATIA失败: {str(e)}")
            return False

    def open_document(self, file_path: str) -> bool:
        try:
            self.part_document = self.documents.open(file_path)
            self._initialize_document_objects()
            return True
        except Exception as e:
            logger.error(f"打开文档失败: {str(e)}")
            return False

    def _initialize_document_objects(self):
        """初始化文档相关的对象"""
        if self.part_document:
            if self.part_document.type == "Part":
                self.part = self.part_document.part
                self.hybrid_bodies = self.part.hybrid_bodies
                self.parameters = self.part.parameters
                self.sketches = self.part.sketches
                self.bodies = self.part.bodies
                self.measure = self.part.measure
                self.analysis = self.part.analysis
            elif self.part_document.type == "Product":
                self.product = self.part_document.product
            elif self.part_document.type == "Drawing":
                self.drawing = self.part_document.drawing

    # 基础文档操作
    def create_new_document(self, doc_type: str) -> tuple[bool, str]:
        try:
            if doc_type == "Part":
                self.part_document = self.documents.add("Part")
            elif doc_type == "Product":
                self.part_document = self.documents.add("Product")
            elif doc_type == "Drawing":
                self.part_document = self.documents.add("Drawing")
            else:
                return False, "不支持的文档类型"
            self._initialize_document_objects()
            return True, "文档创建成功"
        except Exception as e:
            logger.error(f"创建文档失败: {str(e)}")
            return False, f"创建文档失败: {str(e)}"

    def save_document(self, file_path: Optional[str] = None) -> tuple[bool, str]:
        try:
            if not self.part_document:
                return False, "没有活动的文档"
            if file_path:
                self.part_document.save_as(file_path)
            else:
                self.part_document.save()
            return True, "文档保存成功"
        except Exception as e:
            logger.error(f"保存文档失败: {str(e)}")
            return False, f"保存文档失败: {str(e)}"

    def close_document(self) -> tuple[bool, str]:
        try:
            if self.part_document:
                self.part_document.close()
                self._reset_document_objects()
                return True, "文档关闭成功"
            return False, "没有活动的文档"
        except Exception as e:
            logger.error(f"关闭文档失败: {str(e)}")
            return False, f"关闭文档失败: {str(e)}"

    def _reset_document_objects(self):
        """重置所有文档相关的对象"""
        self.part_document = None
        self.part = None
        self.hybrid_bodies = None
        self.parameters = None
        self.sketches = None
        self.bodies = None
        self.measure = None
        self.analysis = None
        self.drawing = None
        self.product = None

    # 参数操作
    def get_parameters(self) -> tuple[bool, Union[List[Dict], str]]:
        try:
            if not self.parameters:
                return False, "没有活动的文档或参数"
            params = []
            for i in range(1, self.parameters.count + 1):
                param = self.parameters.item(i)
                params.append({
                    "name": param.name,
                    "value": param.value,
                    "type": param.type
                })
            return True, params
        except Exception as e:
            logger.error(f"获取参数失败: {str(e)}")
            return False, f"获取参数失败: {str(e)}"

    def set_parameter(self, name: str, value: Any) -> tuple[bool, str]:
        try:
            if not self.parameters:
                return False, "没有活动的文档或参数"
            param = self.parameters.item(name)
            param.value = value
            return True, "参数设置成功"
        except Exception as e:
            logger.error(f"设置参数失败: {str(e)}")
            return False, f"设置参数失败: {str(e)}"

    # 几何操作
    def create_point(self, x: float, y: float, z: float) -> tuple[bool, str]:
        try:
            if not self.hybrid_bodies:
                return False, "没有活动的文档或几何体"
            point = self.hybrid_bodies.add()
            point.add_point(x, y, z)
            return True, "点创建成功"
        except Exception as e:
            logger.error(f"创建点失败: {str(e)}")
            return False, f"创建点失败: {str(e)}"

    def create_line(self, start_point: List[float], end_point: List[float]) -> tuple[bool, str]:
        try:
            if not self.hybrid_bodies:
                return False, "没有活动的文档或几何体"
            line = self.hybrid_bodies.add()
            line.add_line(start_point, end_point)
            return True, "线创建成功"
        except Exception as e:
            logger.error(f"创建线失败: {str(e)}")
            return False, f"创建线失败: {str(e)}"

    def create_plane(self, origin: List[float], normal: List[float]) -> tuple[bool, str]:
        try:
            if not self.hybrid_bodies:
                return False, "没有活动的文档或几何体"
            plane = self.hybrid_bodies.add()
            plane.add_plane(origin, normal)
            return True, "平面创建成功"
        except Exception as e:
            logger.error(f"创建平面失败: {str(e)}")
            return False, f"创建平面失败: {str(e)}"

    # 草图操作
    def create_sketch(self, plane: Any) -> tuple[bool, str]:
        try:
            if not self.sketches:
                return False, "没有活动的文档或草图"
            sketch = self.sketches.add(plane)
            return True, "草图创建成功"
        except Exception as e:
            logger.error(f"创建草图失败: {str(e)}")
            return False, f"创建草图失败: {str(e)}"

    def add_line_to_sketch(self, sketch: Any, start_point: List[float], end_point: List[float]) -> tuple[bool, str]:
        try:
            if not sketch:
                return False, "草图不存在"
            line = sketch.add_line(start_point, end_point)
            return True, "线添加成功"
        except Exception as e:
            logger.error(f"添加线失败: {str(e)}")
            return False, f"添加线失败: {str(e)}"

    def add_circle_to_sketch(self, sketch: Any, center: List[float], radius: float) -> tuple[bool, str]:
        try:
            if not sketch:
                return False, "草图不存在"
            circle = sketch.add_circle(center, radius)
            return True, "圆添加成功"
        except Exception as e:
            logger.error(f"添加圆失败: {str(e)}")
            return False, f"添加圆失败: {str(e)}"

    # 特征操作
    def create_pad(self, sketch: Any, length: float) -> tuple[bool, str]:
        try:
            if not self.bodies:
                return False, "没有活动的文档或实体"
            pad = self.bodies.add_pad(sketch, length)
            return True, "凸台创建成功"
        except Exception as e:
            logger.error(f"创建凸台失败: {str(e)}")
            return False, f"创建凸台失败: {str(e)}"

    def create_pocket(self, sketch: Any, length: float) -> tuple[bool, str]:
        try:
            if not self.bodies:
                return False, "没有活动的文档或实体"
            pocket = self.bodies.add_pocket(sketch, length)
            return True, "凹槽创建成功"
        except Exception as e:
            logger.error(f"创建凹槽失败: {str(e)}")
            return False, f"创建凹槽失败: {str(e)}"

    def create_revolution(self, sketch: Any, angle: float) -> tuple[bool, str]:
        try:
            if not self.bodies:
                return False, "没有活动的文档或实体"
            revolution = self.bodies.add_revolution(sketch, angle)
            return True, "旋转体创建成功"
        except Exception as e:
            logger.error(f"创建旋转体失败: {str(e)}")
            return False, f"创建旋转体失败: {str(e)}"

    # 装配操作
    def add_component(self, file_path: str, position: List[float] = [0, 0, 0]) -> tuple[bool, str]:
        try:
            if not self.product:
                return False, "当前文档不是装配体"
            component = self.product.add_component(file_path)
            component.move(position)
            return True, "组件添加成功"
        except Exception as e:
            logger.error(f"添加组件失败: {str(e)}")
            return False, f"添加组件失败: {str(e)}"

    def create_constraint(self, component1: str, component2: str, constraint_type: str, 
                         reference1: Any, reference2: Any) -> tuple[bool, str]:
        try:
            if not self.product:
                return False, "当前文档不是装配体"
            constraint = self.product.add_constraint(component1, component2, constraint_type, reference1, reference2)
            return True, "约束创建成功"
        except Exception as e:
            logger.error(f"创建约束失败: {str(e)}")
            return False, f"创建约束失败: {str(e)}"

    # 测量操作
    def measure_distance(self, point1: List[float], point2: List[float]) -> tuple[bool, Union[Dict, str]]:
        try:
            if not self.measure:
                return False, "没有活动的文档或测量工具"
            distance = self.measure.distance(point1, point2)
            return True, {"distance": distance}
        except Exception as e:
            logger.error(f"测量距离失败: {str(e)}")
            return False, f"测量距离失败: {str(e)}"

    def measure_angle(self, line1: Any, line2: Any) -> tuple[bool, Union[Dict, str]]:
        try:
            if not self.measure:
                return False, "没有活动的文档或测量工具"
            angle = self.measure.angle(line1, line2)
            return True, {"angle": angle}
        except Exception as e:
            logger.error(f"测量角度失败: {str(e)}")
            return False, f"测量角度失败: {str(e)}"

    def measure_area(self, face: Any) -> tuple[bool, Union[Dict, str]]:
        try:
            if not self.measure:
                return False, "没有活动的文档或测量工具"
            area = self.measure.area(face)
            return True, {"area": area}
        except Exception as e:
            logger.error(f"测量面积失败: {str(e)}")
            return False, f"测量面积失败: {str(e)}"

    def measure_volume(self, body: Any) -> tuple[bool, Union[Dict, str]]:
        try:
            if not self.measure:
                return False, "没有活动的文档或测量工具"
            volume = self.measure.volume(body)
            return True, {"volume": volume}
        except Exception as e:
            logger.error(f"测量体积失败: {str(e)}")
            return False, f"测量体积失败: {str(e)}"

    # 分析操作
    def analyze_mass(self, body: Any) -> tuple[bool, Union[Dict, str]]:
        try:
            if not self.analysis:
                return False, "没有活动的文档或分析工具"
            mass = self.analysis.mass(body)
            return True, {"mass": mass}
        except Exception as e:
            logger.error(f"质量分析失败: {str(e)}")
            return False, f"质量分析失败: {str(e)}"

    def check_interference(self, body1: Any, body2: Any) -> tuple[bool, Union[Dict, str]]:
        try:
            if not self.analysis:
                return False, "没有活动的文档或分析工具"
            interference = self.analysis.interference(body1, body2)
            return True, {"interference": interference}
        except Exception as e:
            logger.error(f"干涉检查失败: {str(e)}")
            return False, f"干涉检查失败: {str(e)}"

    # 工程图操作
    def create_drawing_view(self, name: str, type: str = "Front") -> tuple[bool, str]:
        try:
            if not self.drawing:
                return False, "没有活动的工程图文档"
            view = self.drawing.views.add(name, type)
            return True, "视图创建成功"
        except Exception as e:
            logger.error(f"创建视图失败: {str(e)}")
            return False, f"创建视图失败: {str(e)}"

    def add_dimension(self, view: Any, reference1: Any, reference2: Any) -> tuple[bool, str]:
        try:
            if not self.drawing:
                return False, "没有活动的工程图文档"
            dimension = view.add_dimension(reference1, reference2)
            return True, "尺寸添加成功"
        except Exception as e:
            logger.error(f"添加尺寸失败: {str(e)}")
            return False, f"添加尺寸失败: {str(e)}"

    # 系统操作
    def get_system_info(self) -> tuple[bool, Union[Dict, str]]:
        try:
            if not self.system:
                return False, "未连接到CATIA"
            info = {
                "version": self.system.version,
                "license": self.system.license,
                "workspace": self.system.workspace
            }
            return True, info
        except Exception as e:
            logger.error(f"获取系统信息失败: {str(e)}")
            return False, f"获取系统信息失败: {str(e)}"

catia_service = CATIAService()

# API资源类
class CATIAConnection(Resource):
    @jwt_required()
    def post(self):
        if catia_service.connect():
            return {"status": "success", "message": "CATIA连接成功"}
        return {"status": "error", "message": "CATIA连接失败"}, 500

class DocumentOperation(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        operation = data.get('operation')
        
        if operation == 'open':
            file_path = data.get('file_path')
            if not file_path:
                return {"status": "error", "message": "未提供文件路径"}, 400
            if catia_service.open_document(file_path):
                return {"status": "success", "message": "文档打开成功"}
            return {"status": "error", "message": "文档打开失败"}, 500
            
        elif operation == 'save':
            file_path = data.get('file_path')
            success, message = catia_service.save_document(file_path)
            return {"status": "success" if success else "error", "message": message}
            
        elif operation == 'create':
            doc_type = data.get('doc_type', 'Part')
            success, message = catia_service.create_new_document(doc_type)
            return {"status": "success" if success else "error", "message": message}
            
        elif operation == 'close':
            success, message = catia_service.close_document()
            return {"status": "success" if success else "error", "message": message}
            
        else:
            return {"status": "error", "message": "不支持的操作"}, 400

class ParameterOperation(Resource):
    @jwt_required()
    def get(self):
        success, result = catia_service.get_parameters()
        if success:
            return {"status": "success", "data": result}
        return {"status": "error", "message": result}, 500

    @jwt_required()
    def post(self):
        data = request.get_json()
        name = data.get('name')
        value = data.get('value')
        
        if not name or value is None:
            return {"status": "error", "message": "参数名称和值不能为空"}, 400
            
        success, message = catia_service.set_parameter(name, value)
        return {"status": "success" if success else "error", "message": message}

class GeometryOperation(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        operation = data.get('operation')
        
        if operation == 'point':
            x = data.get('x')
            y = data.get('y')
            z = data.get('z')
            if None in (x, y, z):
                return {"status": "error", "message": "点的坐标不能为空"}, 400
            success, message = catia_service.create_point(x, y, z)
            return {"status": "success" if success else "error", "message": message}
            
        elif operation == 'line':
            start = data.get('start_point')
            end = data.get('end_point')
            if not start or not end:
                return {"status": "error", "message": "线的起点和终点不能为空"}, 400
            success, message = catia_service.create_line(start, end)
            return {"status": "success" if success else "error", "message": message}
            
        elif operation == 'plane':
            origin = data.get('origin')
            normal = data.get('normal')
            if not origin or not normal:
                return {"status": "error", "message": "平面的原点和法向量不能为空"}, 400
            success, message = catia_service.create_plane(origin, normal)
            return {"status": "success" if success else "error", "message": message}
            
        else:
            return {"status": "error", "message": "不支持的操作"}, 400

class SketchOperation(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        operation = data.get('operation')
        
        if operation == 'create':
            plane = data.get('plane')
            if not plane:
                return {"status": "error", "message": "平面不能为空"}, 400
            success, message = catia_service.create_sketch(plane)
            return {"status": "success" if success else "error", "message": message}
            
        elif operation == 'add_line':
            sketch = data.get('sketch')
            start_point = data.get('start_point')
            end_point = data.get('end_point')
            if None in (sketch, start_point, end_point):
                return {"status": "error", "message": "参数不完整"}, 400
            success, message = catia_service.add_line_to_sketch(sketch, start_point, end_point)
            return {"status": "success" if success else "error", "message": message}
            
        elif operation == 'add_circle':
            sketch = data.get('sketch')
            center = data.get('center')
            radius = data.get('radius')
            if None in (sketch, center, radius):
                return {"status": "error", "message": "参数不完整"}, 400
            success, message = catia_service.add_circle_to_sketch(sketch, center, radius)
            return {"status": "success" if success else "error", "message": message}
            
        else:
            return {"status": "error", "message": "不支持的操作"}, 400

class FeatureOperation(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        operation = data.get('operation')
        
        if operation == 'pad':
            sketch = data.get('sketch')
            length = data.get('length')
            if None in (sketch, length):
                return {"status": "error", "message": "参数不完整"}, 400
            success, message = catia_service.create_pad(sketch, length)
            return {"status": "success" if success else "error", "message": message}
            
        elif operation == 'pocket':
            sketch = data.get('sketch')
            length = data.get('length')
            if None in (sketch, length):
                return {"status": "error", "message": "参数不完整"}, 400
            success, message = catia_service.create_pocket(sketch, length)
            return {"status": "success" if success else "error", "message": message}
            
        elif operation == 'revolution':
            sketch = data.get('sketch')
            angle = data.get('angle')
            if None in (sketch, angle):
                return {"status": "error", "message": "参数不完整"}, 400
            success, message = catia_service.create_revolution(sketch, angle)
            return {"status": "success" if success else "error", "message": message}
            
        else:
            return {"status": "error", "message": "不支持的操作"}, 400

class AssemblyOperation(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        operation = data.get('operation')
        
        if operation == 'add_component':
            file_path = data.get('file_path')
            position = data.get('position', [0, 0, 0])
            if not file_path:
                return {"status": "error", "message": "组件文件路径不能为空"}, 400
            success, message = catia_service.add_component(file_path, position)
            return {"status": "success" if success else "error", "message": message}
            
        elif operation == 'create_constraint':
            component1 = data.get('component1')
            component2 = data.get('component2')
            constraint_type = data.get('constraint_type')
            reference1 = data.get('reference1')
            reference2 = data.get('reference2')
            
            if None in (component1, component2, constraint_type, reference1, reference2):
                return {"status": "error", "message": "约束参数不完整"}, 400
                
            success, message = catia_service.create_constraint(
                component1, component2, constraint_type, reference1, reference2
            )
            return {"status": "success" if success else "error", "message": message}
            
        else:
            return {"status": "error", "message": "不支持的操作"}, 400

class MeasureOperation(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        operation = data.get('operation')
        
        if operation == 'distance':
            point1 = data.get('point1')
            point2 = data.get('point2')
            if None in (point1, point2):
                return {"status": "error", "message": "参数不完整"}, 400
            success, result = catia_service.measure_distance(point1, point2)
            if success:
                return {"status": "success", "data": result}
            return {"status": "error", "message": result}, 500
            
        elif operation == 'angle':
            line1 = data.get('line1')
            line2 = data.get('line2')
            if None in (line1, line2):
                return {"status": "error", "message": "参数不完整"}, 400
            success, result = catia_service.measure_angle(line1, line2)
            if success:
                return {"status": "success", "data": result}
            return {"status": "error", "message": result}, 500
            
        elif operation == 'area':
            face = data.get('face')
            if not face:
                return {"status": "error", "message": "面不能为空"}, 400
            success, result = catia_service.measure_area(face)
            if success:
                return {"status": "success", "data": result}
            return {"status": "error", "message": result}, 500
            
        elif operation == 'volume':
            body = data.get('body')
            if not body:
                return {"status": "error", "message": "实体不能为空"}, 400
            success, result = catia_service.measure_volume(body)
            if success:
                return {"status": "success", "data": result}
            return {"status": "error", "message": result}, 500
            
        else:
            return {"status": "error", "message": "不支持的操作"}, 400

class AnalysisOperation(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        operation = data.get('operation')
        
        if operation == 'mass':
            body = data.get('body')
            if not body:
                return {"status": "error", "message": "实体不能为空"}, 400
            success, result = catia_service.analyze_mass(body)
            if success:
                return {"status": "success", "data": result}
            return {"status": "error", "message": result}, 500
            
        elif operation == 'interference':
            body1 = data.get('body1')
            body2 = data.get('body2')
            if None in (body1, body2):
                return {"status": "error", "message": "参数不完整"}, 400
            success, result = catia_service.check_interference(body1, body2)
            if success:
                return {"status": "success", "data": result}
            return {"status": "error", "message": result}, 500
            
        else:
            return {"status": "error", "message": "不支持的操作"}, 400

class DrawingOperation(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        operation = data.get('operation')
        
        if operation == 'create_view':
            name = data.get('name')
            view_type = data.get('type', 'Front')
            if not name:
                return {"status": "error", "message": "视图名称不能为空"}, 400
            success, message = catia_service.create_drawing_view(name, view_type)
            return {"status": "success" if success else "error", "message": message}
            
        elif operation == 'add_dimension':
            view = data.get('view')
            reference1 = data.get('reference1')
            reference2 = data.get('reference2')
            if None in (view, reference1, reference2):
                return {"status": "error", "message": "参数不完整"}, 400
            success, message = catia_service.add_dimension(view, reference1, reference2)
            return {"status": "success" if success else "error", "message": message}
            
        else:
            return {"status": "error", "message": "不支持的操作"}, 400

class SystemOperation(Resource):
    @jwt_required()
    def get(self):
        success, result = catia_service.get_system_info()
        if success:
            return {"status": "success", "data": result}
        return {"status": "error", "message": result}, 500

# 注册API路由
api.add_resource(CATIAConnection, '/api/catia/connect')
api.add_resource(DocumentOperation, '/api/catia/document')
api.add_resource(ParameterOperation, '/api/catia/parameters')
api.add_resource(GeometryOperation, '/api/catia/geometry')
api.add_resource(SketchOperation, '/api/catia/sketch')
api.add_resource(FeatureOperation, '/api/catia/feature')
api.add_resource(AssemblyOperation, '/api/catia/assembly')
api.add_resource(MeasureOperation, '/api/catia/measure')
api.add_resource(AnalysisOperation, '/api/catia/analysis')
api.add_resource(DrawingOperation, '/api/catia/drawing')
api.add_resource(SystemOperation, '/api/catia/system')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 