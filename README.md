# Video Toolkit

MP4 동영상 프레임 추출 및 동영상 합치기 도구

## 기능

### 프레임 추출
- 마지막 프레임 추출
- 특정 시간대 프레임 추출
- 특정 시간대 ±1초 범위 추출
- 프레임 번호로 추출
- 전체 프레임 추출

### 동영상 합치기
- 두 개의 동영상을 하나로 합치기
- 자동 해상도/FPS 조정
- 자동 파일명 생성 (중복 시 숫자 증가)
- ※ OpenCV 사용으로 음성은 포함되지 않음 (동영상만)

## 다운로드

[Releases](https://github.com/YOUR_USERNAME/mov_make/releases) 페이지에서 최신 버전의 `VideoToolkit.exe` 다운로드

## 사용 방법

### EXE 실행 (권장)
1. Release 페이지에서 `VideoToolkit.exe` 다운로드
2. 더블클릭으로 실행
3. Python 설치 불필요

### 소스코드 실행
```bash
# 가상환경 생성 및 활성화
python -m venv .venv
.venv\Scripts\activate  # Windows

# 의존성 설치
pip install opencv-python numpy

# 실행
python video_frame_extractor.py
```

## EXE 빌드 방법

```bash
# PyInstaller 설치
pip install pyinstaller

# 빌드 스크립트 실행
build_exe.bat

# 또는 직접 빌드
pyinstaller --onefile --windowed --name="VideoToolkit" video_frame_extractor.py
```

빌드된 EXE 파일은 `dist/VideoToolkit.exe`에 생성됩니다.

## GitHub Release 배포 방법

1. **EXE 빌드**
   ```bash
   build_exe.bat
   ```

2. **GitHub Release 생성**
   - GitHub 저장소 → Releases → "Create a new release"
   - Tag 생성 (예: v1.0.0)
   - Release title 입력
   - `dist/VideoToolkit.exe` 파일 업로드
   - "Publish release" 클릭

3. **사용자는 Release 페이지에서 다운로드**

## 요구사항

- Windows 10/11
- (소스코드 실행 시) Python 3.7+
- (소스코드 실행 시) opencv-python, numpy

## 라이센스

MIT License
