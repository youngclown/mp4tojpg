import cv2
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import os
import numpy as np


class VideoFrameExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("MP4 프레임 추출기")
        self.root.geometry("600x500")

        self.video_path = None
        self.video_duration = 0
        self.fps = 0
        self.total_frames = 0

        self.setup_ui()

    def setup_ui(self):
        # 파일 선택 프레임
        file_frame = ttk.LabelFrame(self.root, text="동영상 파일 선택", padding=10)
        file_frame.pack(fill="x", padx=10, pady=5)

        self.file_label = ttk.Label(file_frame, text="선택된 파일 없음")
        self.file_label.pack(side="left", fill="x", expand=True)

        ttk.Button(file_frame, text="파일 선택", command=self.select_file).pack(side="right")

        # 동영상 정보 프레임
        info_frame = ttk.LabelFrame(self.root, text="동영상 정보", padding=10)
        info_frame.pack(fill="x", padx=10, pady=5)

        self.info_label = ttk.Label(info_frame, text="파일을 선택하세요")
        self.info_label.pack()

        # 추출 모드 선택
        mode_frame = ttk.LabelFrame(self.root, text="추출 모드", padding=10)
        mode_frame.pack(fill="x", padx=10, pady=5)

        self.mode_var = tk.StringVar(value="last")

        ttk.Radiobutton(mode_frame, text="마지막 프레임", variable=self.mode_var,
                       value="last", command=self.update_mode).pack(anchor="w")
        ttk.Radiobutton(mode_frame, text="특정 시간대 (초 단위)", variable=self.mode_var,
                       value="time", command=self.update_mode).pack(anchor="w")
        ttk.Radiobutton(mode_frame, text="특정 시간대 ±1초", variable=self.mode_var,
                       value="range", command=self.update_mode).pack(anchor="w")
        ttk.Radiobutton(mode_frame, text="프레임 번호 지정", variable=self.mode_var,
                       value="frame", command=self.update_mode).pack(anchor="w")
        ttk.Radiobutton(mode_frame, text="전체 프레임 (모든 프레임)", variable=self.mode_var,
                       value="all", command=self.update_mode).pack(anchor="w")

        # 입력 프레임
        input_frame = ttk.LabelFrame(self.root, text="추출 설정", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        self.input_label = ttk.Label(input_frame, text="")
        self.input_label.pack(anchor="w")

        self.input_entry = ttk.Entry(input_frame, width=20)
        self.input_entry.pack(anchor="w", pady=5)
        self.input_entry.config(state="disabled")

        # 저장 경로 프레임
        output_frame = ttk.LabelFrame(self.root, text="저장 경로", padding=10)
        output_frame.pack(fill="x", padx=10, pady=5)

        self.output_label = ttk.Label(output_frame, text="동영상과 같은 폴더에 저장")
        self.output_label.pack(side="left", fill="x", expand=True)

        ttk.Button(output_frame, text="경로 변경", command=self.select_output).pack(side="right")

        self.output_path = None

        # 실행 버튼
        ttk.Button(self.root, text="프레임 추출", command=self.extract_frames,
                  style="Accent.TButton").pack(pady=20)

        # 진행 상태
        self.progress_label = ttk.Label(self.root, text="")
        self.progress_label.pack()

        self.progress = ttk.Progressbar(self.root, mode='determinate')
        self.progress.pack(fill="x", padx=10, pady=5)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="MP4 파일 선택",
            filetypes=[("MP4 파일", "*.mp4"), ("모든 파일", "*.*")]
        )

        if file_path:
            self.video_path = file_path
            self.file_label.config(text=Path(file_path).name)

            # 동영상 정보 가져오기
            cap = cv2.VideoCapture(file_path)
            self.fps = cap.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.video_duration = self.total_frames / self.fps if self.fps > 0 else 0
            cap.release()

            self.info_label.config(
                text=f"FPS: {self.fps:.2f} | 총 프레임: {self.total_frames} | "
                     f"길이: {self.video_duration:.2f}초"
            )

            # 기본 저장 경로 설정
            self.output_path = str(Path(file_path).parent)

    def select_output(self):
        folder = filedialog.askdirectory(title="저장 폴더 선택")
        if folder:
            self.output_path = folder
            self.output_label.config(text=folder)

    def update_mode(self):
        mode = self.mode_var.get()

        if mode == "last":
            self.input_entry.config(state="disabled")
            self.input_label.config(text="")
        elif mode == "time":
            self.input_entry.config(state="normal")
            self.input_label.config(text=f"시간 입력 (초, 0-{self.video_duration:.2f}):")
        elif mode == "range":
            self.input_entry.config(state="normal")
            self.input_label.config(text=f"중심 시간 입력 (초, 1-{self.video_duration-1:.2f}):")
        elif mode == "frame":
            self.input_entry.config(state="normal")
            self.input_label.config(text=f"프레임 번호 입력 (0-{self.total_frames-1}):")
        elif mode == "all":
            self.input_entry.config(state="disabled")
            self.input_label.config(text="")

    def extract_frames(self):
        if not self.video_path:
            messagebox.showerror("오류", "동영상 파일을 선택하세요")
            return

        if not self.output_path:
            messagebox.showerror("오류", "저장 경로를 선택하세요")
            return

        mode = self.mode_var.get()

        try:
            cap = cv2.VideoCapture(self.video_path)
            video_name = Path(self.video_path).stem

            if mode == "last":
                self.extract_last_frame(cap, video_name)

            elif mode == "time":
                time_sec = float(self.input_entry.get())
                if time_sec < 0 or time_sec > self.video_duration:
                    raise ValueError(f"시간은 0~{self.video_duration:.2f} 사이여야 합니다")
                self.extract_frame_at_time(cap, video_name, time_sec)

            elif mode == "range":
                time_sec = float(self.input_entry.get())
                if time_sec < 1 or time_sec > self.video_duration - 1:
                    raise ValueError(f"시간은 1~{self.video_duration-1:.2f} 사이여야 합니다")
                self.extract_frame_range(cap, video_name, time_sec)

            elif mode == "frame":
                frame_num = int(self.input_entry.get())
                if frame_num < 0 or frame_num >= self.total_frames:
                    raise ValueError(f"프레임 번호는 0~{self.total_frames-1} 사이여야 합니다")
                self.extract_specific_frame(cap, video_name, frame_num)

            elif mode == "all":
                self.extract_all_frames(cap, video_name)

            cap.release()
            messagebox.showinfo("완료", "프레임 추출이 완료되었습니다!")
            self.progress_label.config(text="")
            self.progress['value'] = 0

        except ValueError as e:
            messagebox.showerror("입력 오류", str(e))
        except Exception as e:
            messagebox.showerror("오류", f"프레임 추출 중 오류 발생:\n{str(e)}")

    def save_frame(self, frame, output_file):
        """프레임을 안전하게 저장하는 헬퍼 함수"""
        try:
            # 한글 경로 지원을 위한 처리
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
            result, encimg = cv2.imencode('.jpg', frame, encode_param)
            if result:
                with open(output_file, mode='wb') as f:
                    f.write(encimg)
                return True
            return False
        except Exception as e:
            print(f"저장 오류: {e}")
            return False

    def extract_last_frame(self, cap, video_name):
        cap.set(cv2.CAP_PROP_POS_FRAMES, self.total_frames - 1)
        ret, frame = cap.read()

        if ret:
            output_file = os.path.join(self.output_path, f"{video_name}_last_frame.jpg")
            if self.save_frame(frame, output_file):
                self.progress_label.config(text=f"저장됨: {Path(output_file).name}")
            else:
                raise Exception("프레임 저장 실패")

    def extract_frame_at_time(self, cap, video_name, time_sec):
        frame_num = int(time_sec * self.fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()

        if ret:
            output_file = os.path.join(self.output_path,
                                      f"{video_name}_time_{time_sec:.2f}s.jpg")
            if self.save_frame(frame, output_file):
                self.progress_label.config(text=f"저장됨: {Path(output_file).name}")
            else:
                raise Exception("프레임 저장 실패")

    def extract_frame_range(self, cap, video_name, center_time):
        start_time = max(0, center_time - 1)
        end_time = min(self.video_duration, center_time + 1)

        start_frame = int(start_time * self.fps)
        end_frame = int(end_time * self.fps)

        total = end_frame - start_frame
        count = 0

        for frame_num in range(start_frame, end_frame):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()

            if ret:
                time_sec = frame_num / self.fps
                output_file = os.path.join(self.output_path,
                                          f"{video_name}_range_{time_sec:.3f}s_frame{frame_num}.jpg")
                if self.save_frame(frame, output_file):
                    count += 1

                self.progress['value'] = (count / total) * 100
                self.progress_label.config(text=f"진행 중: {count}/{total} 프레임")
                self.root.update_idletasks()

        self.progress_label.config(text=f"완료: {count}개 프레임 저장됨")

    def extract_specific_frame(self, cap, video_name, frame_num):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()

        if ret:
            output_file = os.path.join(self.output_path,
                                      f"{video_name}_frame_{frame_num}.jpg")
            if self.save_frame(frame, output_file):
                self.progress_label.config(text=f"저장됨: {Path(output_file).name}")
            else:
                raise Exception("프레임 저장 실패")

    def extract_all_frames(self, cap, video_name):
        frame_num = 0
        count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            output_file = os.path.join(self.output_path,
                                      f"{video_name}_frame_{frame_num:06d}.jpg")
            if self.save_frame(frame, output_file):
                count += 1
            frame_num += 1

            if frame_num % 10 == 0:
                self.progress['value'] = (frame_num / self.total_frames) * 100
                self.progress_label.config(text=f"진행 중: {frame_num}/{self.total_frames} 프레임")
                self.root.update_idletasks()

        self.progress_label.config(text=f"완료: {count}개 프레임 저장됨")


def main():
    root = tk.Tk()
    app = VideoFrameExtractor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
