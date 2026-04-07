"""
跌倒检测器 - ONNX版本

使用跌倒检测模型 + MediaPipe人脸检测 + ByteTrack跟踪
返回检测数据，后端自行处理业务逻辑
"""
import cv2
import numpy as np
import onnxruntime as ort
import mediapipe as mp
from typing import Optional, List
from pathlib import Path

from .types import FrameResult, PersonResult, SessionResult
from .session import SessionManager


class FallDetector:
    """
    跌倒检测器

    使用方式:
        detector = FallDetector()

        # 创建视频会话
        video_id = detector.create_session()

        # 处理帧
        result = detector.process_frame(video_id, frame)
        for p in result.frame_result.persons:
            print(f"ID={p.person_id}, class={p.class_name}, movement={p.movement}")

        # 结束会话
        detector.close_session(video_id)
    """

    # 单帧最多检测人数
    MAX_PERSONS = 3

    # 类别名称映射
    CLASS_NAMES = {0: 'normal', 1: 'fallen'}

    # 人脸模糊配置
    ENABLE_FACE_BLUR = True
    FACE_BLUR_STRENGTH = 51
    FACE_BLUR_EXPAND_RATIO = 0.5

    def __init__(self,
                 model_path: str = "core/models/fall_detection_v5.onnx",
                 conf_threshold: float = 0.3,
                 tracker_fps: float = 25.0,
                 providers: list = None):
        """
        初始化检测器

        Args:
            model_path: ONNX模型路径
            conf_threshold: 检测置信度阈值
            tracker_fps: 追踪器预期帧率
            providers: ONNX Runtime providers
        """
        self.model_path = model_path
        self.conf_threshold = conf_threshold

        # ONNX推理
        if providers is None:
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        self.session = ort.InferenceSession(model_path, providers=providers)
        self.input_name = self.session.get_inputs()[0].name
        self.img_size = self.session.get_inputs()[0].shape[2]

        # MediaPipe 人脸检测器 (全距模型)
        self._init_mediapipe()

        # 会话管理（追踪）
        self.session_manager = SessionManager(tracker_fps=tracker_fps)

        # 保存原始图像尺寸
        self.orig_shape = None

    def _init_mediapipe(self):
        """初始化MediaPipe人脸检测"""
        model_path = Path(__file__).parent / "models" / "blaze_face_full_range.tflite"
        if not model_path.exists():
            raise FileNotFoundError(
                f"MediaPipe模型不存在: {model_path}\n"
                "请手动下载: https://storage.googleapis.com/mediapipe-models/"
                "face_detector/blaze_face_full_range/float16/1/blaze_face_full_range.tflite"
            )

        BaseOptions = mp.tasks.BaseOptions
        FaceDetector = mp.tasks.vision.FaceDetector
        FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        self.mp_options = FaceDetectorOptions(
            base_options=BaseOptions(model_asset_path=str(model_path)),
            running_mode=VisionRunningMode.IMAGE,
            min_detection_confidence=0.5
        )
        self.mp_detector = FaceDetector.create_from_options(self.mp_options)

    # ==================== 接口 ====================

    def create_session(self) -> str:
        """创建新的视频会话"""
        return self.session_manager.create_session()

    def process_frame(self, video_id: str, frame: np.ndarray) -> SessionResult:
        """
        处理单帧图像

        Args:
            video_id: 会话ID
            frame: BGR图像

        Returns:
            SessionResult: 包含检测结果、处理后的帧
        """
        # 1. 检测单帧（实时监控时过滤顶部/底部10%区域）
        frame_result = self._detect_single(frame, video_id)

        # 2. 追踪 + 计算 movement（先于人脸模糊，需要跟踪的人体框）
        frame_result = self.session_manager.process(video_id, frame_result, frame)

        # 3. 人脸模糊（使用跟踪后的人体框）
        processed_frame = frame.copy()
        if self.ENABLE_FACE_BLUR and frame_result.detected:
            processed_frame = self._apply_face_blur(video_id, processed_frame, frame_result.persons)

        return SessionResult(
            video_id=video_id,
            frame_result=frame_result,
            processed_frame=processed_frame
        )

    async def process_frame_async(self, video_id: str, frame: np.ndarray) -> SessionResult:
        """处理单帧图像（异步版本）"""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process_frame, video_id, frame)

    def close_session(self, video_id: str) -> bool:
        """关闭会话"""
        return self.session_manager.close_session(video_id)

    # ==================== 内部方法 ====================

    def _preprocess(self, frame: np.ndarray) -> np.ndarray:
        """预处理图像"""
        self.orig_shape = frame.shape[:2]
        img = cv2.resize(frame, (self.img_size, self.img_size))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.transpose(2, 0, 1)
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)
        return img

    def _postprocess(self, outputs: tuple) -> List[tuple]:
        """
        后处理模型输出

        YOLO11 ONNX 输出格式：[1, 6, 2100]
        每个锚点 6 维：[cx, cy, w, h, class0_score, class1_score]
        其中 class0=normal, class1=fallen，均为 sigmoid 后的概率值。

        Returns:
            [(box, class_id, score), ...]  经过 NMS 后的结果
        """
        pred = outputs[0]  # (1, 6, 2100)

        # 转置 (1, 6, 2100) -> (2100, 6)
        if pred.shape[1] == 6:
            pred = pred.transpose(0, 2, 1)
        pred = pred[0]  # (2100, 6)

        # 取各锚点最高类别分数及对应类别
        class_scores = pred[:, 4:]          # (2100, 2)
        class_ids = np.argmax(class_scores, axis=1)    # (2100,)
        scores = class_scores[np.arange(len(pred)), class_ids]  # (2100,)

        # 过滤低置信度
        mask = scores > self.conf_threshold
        pred = pred[mask]
        scores = scores[mask]
        class_ids = class_ids[mask]

        if len(pred) == 0:
            return []

        scale_h = self.orig_shape[0] / self.img_size
        scale_w = self.orig_shape[1] / self.img_size

        # 将 cx,cy,w,h 转为 x1,y1,x2,y2（原图坐标）
        cx, cy, w, h = pred[:, 0], pred[:, 1], pred[:, 2], pred[:, 3]
        x1 = (cx - w / 2) * scale_w
        y1 = (cy - h / 2) * scale_h
        x2 = (cx + w / 2) * scale_w
        y2 = (cy + h / 2) * scale_h
        boxes = np.stack([x1, y1, x2, y2], axis=1)  # (N, 4)

        # NMS：用 OpenCV，输入格式为 [x, y, w, h]
        boxes_xywh = np.stack([x1, y1, x2 - x1, y2 - y1], axis=1)
        indices = cv2.dnn.NMSBoxes(
            boxes_xywh.tolist(),
            scores.tolist(),
            score_threshold=self.conf_threshold,
            nms_threshold=0.45,
        )

        if len(indices) == 0:
            return []

        # cv2.dnn.NMSBoxes 返回值在不同版本中可能为 (N,1) 或 (N,)
        indices = np.array(indices).flatten()

        # 按置信度降序，最多取 MAX_PERSONS 个
        indices = sorted(indices, key=lambda i: scores[i], reverse=True)[:self.MAX_PERSONS]

        results = []
        for idx in indices:
            box = [float(boxes[idx, 0]), float(boxes[idx, 1]),
                   float(boxes[idx, 2]), float(boxes[idx, 3])]
            results.append((box, int(class_ids[idx]), float(scores[idx])))

        return results

    def _detect_single(self, frame: np.ndarray, video_id: str = None) -> FrameResult:
        """单帧检测"""
        img = self._preprocess(frame)
        outputs = self.session.run(None, {self.input_name: img})
        detections = self._postprocess(outputs)

        if not detections:
            return FrameResult(detected=False, persons=[])

        # 检查是否为实时监控会话（仅实时监控时过滤顶部/底部10%区域）
        is_live = False
        if video_id:
            try:
                from detect.risk_engine import risk_engine
                session = risk_engine._sessions.get(video_id)
                if session and session.is_live:
                    is_live = True
            except ImportError:
                pass

        # 过滤顶部10%和底部10%区域的检测框（仅实时监控）
        if is_live:
            h = self.orig_shape[0]  # 原图高度
            top_boundary = h * 0.1
            bottom_boundary = h * 0.9

            filtered_detections = []
            for box, class_id, score in detections:
                # 检测框中心点Y坐标
                center_y = (box[1] + box[3]) / 2
                # 只保留中心点在有效区域内的检测框
                if top_boundary <= center_y <= bottom_boundary:
                    filtered_detections.append((box, class_id, score))
            detections = filtered_detections

        if not detections:
            return FrameResult(detected=False, persons=[])

        persons = []
        for i, (box, class_id, score) in enumerate(detections):
            class_name = self.CLASS_NAMES.get(class_id, 'unknown')

            persons.append(PersonResult(
                person_id=i,  # 临时ID，追踪后会更新
                class_id=class_id,
                class_name=class_name,
                confidence=score,
                box=box,
                movement=None
            ))

        return FrameResult(detected=True, persons=persons)

    def _apply_face_blur(self, video_id: str, frame: np.ndarray,
                          persons: List[PersonResult]) -> np.ndarray:
        """
        使用MediaPipe检测人脸并模糊，结合ByteTrack跟踪推断

        Args:
            video_id: 会话ID
            frame: BGR图像
            persons: 跟踪后的人员列表

        Returns:
            模糊后的帧
        """
        h, w = frame.shape[:2]

        # MediaPipe检测人脸
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        mp_result = self.mp_detector.detect(mp_img)

        # 收集检测到的人脸
        detected_faces = []
        if mp_result.detections:
            for det in mp_result.detections:
                bbox = det.bounding_box
                x, y, fw, fh = int(bbox.origin_x), int(bbox.origin_y), int(bbox.width), int(bbox.height)
                detected_faces.append([x, y, x + fw, y + fh])

        # 为每个跟踪的人分配人脸
        for person in persons:
            body_box = person.box
            person_id = person.person_id

            # 尝试匹配检测到的人脸
            matched_face = self._match_face_to_body(detected_faces, body_box, w, h)

            if matched_face is not None:
                # MediaPipe检测到人脸，记录相对位置
                self.session_manager.update_face_position(video_id, person_id, body_box, matched_face)
                self._blur_region(frame, matched_face, w, h)
            else:
                # 漏检，尝试用跟踪推断
                inferred_face = self.session_manager.get_face_position(video_id, person_id, body_box)

                if inferred_face is not None:
                    self._blur_region(frame, inferred_face, w, h)
                    self.session_manager.mark_face_lost(video_id, person_id)

        return frame

    def _match_face_to_body(self, faces: List[List[int]], body_box: List[float],
                               frame_w: int, frame_h: int) -> Optional[List[float]]:
        """
        将检测到的人脸匹配到人体框

        优先选择在人体框上半部分的人脸
        """
        if not faces:
            return None

        body_x1, body_y1, body_x2, body_y2 = body_box
        body_cx = (body_x1 + body_x2) / 2
        body_top_half_y = body_y1 + (body_y2 - body_y1) * 0.6  # 上60%区域

        best_face = None
        best_score = -1

        for face in faces:
            fx1, fy1, fx2, fy2 = face
            face_cx = (fx1 + fx2) / 2
            face_cy = (fy1 + fy2) / 2

            # 人脸中心应在人体框内
            if not (body_x1 <= face_cx <= body_x2 and body_y1 <= face_cy <= body_y2):
                continue

            # 人脸应在人体框上半部分
            if face_cy > body_top_half_y:
                continue

            # 计算匹配分数（越靠近人体框中心越好）
            score = 1 - abs(face_cx - body_cx) / (body_x2 - body_x1)
            if score > best_score:
                best_score = score
                best_face = [fx1, fy1, fx2, fy2]

        return best_face

    def _blur_region(self, frame: np.ndarray, box: List[float],
                        frame_w: int, frame_h: int):
        """对指定区域进行模糊"""
        # 扩大模糊区域
        expand = self.FACE_BLUR_EXPAND_RATIO
        x1, y1, x2, y2 = box
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        fw, fh = x2 - x1, y2 - y1

        new_w = int(fw * (1 + expand))
        new_h = int(fh * (1 + expand))

        x1 = max(0, int(cx - new_w / 2))
        y1 = max(0, int(cy - new_h / 2))
        x2 = min(frame_w, int(cx + new_w / 2))
        y2 = min(frame_h, int(cy + new_h / 2))

        if x2 - x1 > 5 and y2 - y1 > 5:
            region = frame[y1:y2, x1:x2]
            blurred = cv2.GaussianBlur(region, (self.FACE_BLUR_STRENGTH, self.FACE_BLUR_STRENGTH), 0)
            frame[y1:y2, x1:x2] = blurred

        return frame