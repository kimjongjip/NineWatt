# Demo
DB에 저장되어 있는 건물 이미지를 불러와, SAM을 통한 건물 분할 및 YOLOv8seg를 통한 가용 공간 추출, 최종 버티포트 수용성 판단을 진행하는 통합 데모의 코드가 포함된 디렉토리입니다.

## 예시 실행 화면
![데모 실행 예시](../images/demo.gif)
1. Drop-Down 메뉴를 통해 후보지 건물의 id를 보여주고, 건물 id 클릭 시 건물 이미지를 가져옵니다.
2. 건물 분할 버튼을 통해 건물 분할을 수행합니다.
3. 가용 공간 버튼을 통해 가용 공간 마스크를 생성합니다. 헬리패드가 있을 경우 헬리패드 사용이 가능하다고 표시해주고, 가용 공간이 없는 경우 버티포트 설치가 불가하다고 표시합니다.
4. 최대 원 계산 버튼으로 마스크 내 최대 넓이의 원을 계산합니다.
5. 최종적으로 원의 지름과 건물의 메타데이터를 통해 버티포트 수용성을 판단합니다.

## 환경 설정
### 1. 모델 가중치 다운로드
- [Google Drive](https://drive.google.com/file/d/1fNrkIfhOnGlnAF9g11uj0PHbQ1rkxtxc/view?usp=drive_link)

### 2. detectron2, SAM 설치
```
pip install git+https://github.com/facebookresearch/segment-anything.git
pip install git+https://github.com/facebookresearch/detectron2.git
```

### 3. 필요 라이브러리 설치
```
pip install torch torchvision torchaudio
pip install opencv-python-headless matplotlib numpy
pip install gradio pillow ultralytics
```

### 4. DB 정보 변경
```
your_host -> DB 호스트 입력
your_password -> DB 비밀번호 입력
```

## 개발 환경
- Ubuntu 22.04 LTS (WSL 2 활용)
- Python 3.10.12

## 라이브러리 사용 버전
- detectron2 0.6
- SAM 1
- YOLOv8seg
- ultralytics 8.3.32
- PIL 10.3.0
- openCV 4.10.0.84
- torch 2.5.1+cu124
- torchvision 0.20.1+cu124
- numpy 1.26.4
- gradio 5.6.0
- psycopg2 2.9.9
- matplotlib 3.8.4

## 사용 모델
```
best.pt (YOLOv8seg)
sam_vit_l_0b3195.pth (SAM)
model_final.pth (Mask-RCNN)
```

## 최종 디렉토리 구조 
```
NineWatt/데모/  
├── images  
│ ├── evtol.png  
├── best.pt    
├── calculate_circle.py  
├── demo.py  
├── get_image.py  
├── maskrcnn_mask_generate.py  (maskRCNN 가용공간 추출)
├── model_final.pth  
├── sam_segment.py  (SAM 건물 분할)
├── sam_vit_l_0b3195.pth  
├── get_image.py  
└── yolo_mask_generate.py (YOLOv8seg 가용공간 추출)
```

## 데모 실행
```
python3 demo.py
```

## 주요 파일 설명
- demo.py : 데모 사이트 실행
- get_image.py : DB에서 이미지 불러오기
- sam_segment.py : SAM을 통한 건물 분할
- yolo_mask_generate.py : YOLOv8seg 모델 통한 가용 공간 마스크 추출
- maskrcnn_mask_generate.py : maskRCNN 모델 통한 가용 공간 마스크 추출 (현재 미사용)
- calculate_circle.py : 마스크 내 최대 원 계산

## Reference
- [Detectron2](https://github.com/facebookresearch/detectron2)
- [Segment Anything](https://github.com/facebookresearch/segment-anything)
- [Gradio](https://www.gradio.app/)
