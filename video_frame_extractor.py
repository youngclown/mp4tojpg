import cv2
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import os
import numpy as np


class VideoFrameExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("MP4 프레임 추출기 & 동영상 합치기")
        self.root.geometry("600x500")

        self.video_path = None
        self.video_duration = 0
        self.fps = 0
        self.total_frames = 0

        # 동영상 합치기용 변수
        self.video1_path = None
        self.video2_path = None
        self.merge_output_path = None

        self.setup_ui()

    def setup_ui(self):
        # 탭 생성
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # 프레임 추출 탭
        extract_tab = ttk.Frame(notebook)
        notebook.add(extract_tab, text="프레임 추출")
        self.setup_extract_tab(extract_tab)

        # 동영상 합치기 탭
        merge_tab = ttk.Frame(notebook)
        notebook.add(merge_tab, text="동영상 합치기")
        self.setup_merge_tab(merge_tab)

    def setup_extract_tab(self, parent):
        # 파일 선택 프레임
        file_frame = ttk.LabelFrame(parent, text="동영상 파일 선택", padding=10)
        file_frame.pack(fill="x", padx=10, pady=5)

        self.file_label = ttk.Label(file_frame, text="선택된 파일 없음")
        self.file_label.pack(side="left", fill="x", expand=True)

        ttk.Button(file_frame, text="파일 선택", command=self.select_file).pack(side="right")

        # 동영상 정보 프레임
        info_frame = ttk.LabelFrame(parent, text="동영상 정보", padding=10)
        info_frame.pack(fill="x", padx=10, pady=5)

        self.info_label = ttk.Label(info_frame, text="파일을 선택하세요")
        self.info_label.pack()

        # 추출 모드 선택
        mode_frame = ttk.LabelFrame(parent, text="추출 모드", padding=10)
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
        input_frame = ttk.LabelFrame(parent, text="추출 설정", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        self.input_label = ttk.Label(input_frame, text="")
        self.input_label.pack(anchor="w")

        self.input_entry = ttk.Entry(input_frame, width=20)
        self.input_entry.pack(anchor="w", pady=5)
        self.input_entry.config(state="disabled")

        # 저장 경로 프레임
        output_frame = ttk.LabelFrame(parent, text="저장 경로", padding=10)
        output_frame.pack(fill="x", padx=10, pady=5)

        self.output_label = ttk.Label(output_frame, text="동영상과 같은 폴더에 저장")
        self.output_label.pack(side="left", fill="x", expand=True)

        ttk.Button(output_frame, text="경로 변경", command=self.select_output).pack(side="right")

        self.output_path = None

        # 실행 버튼
        ttk.Button(parent, text="프레임 추출", command=self.extract_frames,
                  style="Accent.TButton").pack(pady=20)

        # 진행 상태
        self.progress_label = ttk.Label(parent, text="")
        self.progress_label.pack()

        self.progress = ttk.Progressbar(parent, mode='determinate')
        self.progress.pack(fill="x", padx=10, pady=5)

    def setup_merge_tab(self, parent):
        # 첫 번째 동영상 선택
        merge_frame1 = ttk.LabelFrame(parent, text="첫 번째 동영상", padding=10)
        merge_frame1.pack(fill="x", padx=10, pady=5)

        self.video1_label = ttk.Label(merge_frame1, text="선택된 파일 없음")
        self.video1_label.pack(side="left", fill="x", expand=True)

        ttk.Button(merge_frame1, text="파일 선택", command=self.select_video1).pack(side="right")

        # 두 번째 동영상 선택
        merge_frame2 = ttk.LabelFrame(parent, text="두 번째 동영상", padding=10)
        merge_frame2.pack(fill="x", padx=10, pady=5)

        self.video2_label = ttk.Label(merge_frame2, text="선택된 파일 없음")
        self.video2_label.pack(side="left", fill="x", expand=True)

        ttk.Button(merge_frame2, text="파일 선택", command=self.select_video2).pack(side="right")

        # 저장 경로 프레임
        merge_output_frame = ttk.LabelFrame(parent, text="저장 경로", padding=10)
        merge_output_frame.pack(fill="x", padx=10, pady=5)

        self.merge_output_label = ttk.Label(merge_output_frame, text="첫 번째 동영상과 같은 폴더에 저장")
        self.merge_output_label.pack(side="left", fill="x", expand=True)

        ttk.Button(merge_output_frame, text="경로 변경", command=self.select_merge_output).pack(side="right")

        # 음성 옵션 선택
        audio_option_frame = ttk.LabelFrame(parent, text="음성 옵션", padding=10)
        audio_option_frame.pack(fill="x", padx=10, pady=5)

        self.include_audio_var = tk.BooleanVar(value=False)

        ttk.Radiobutton(audio_option_frame, text="동영상만 (음성 없음)",
                       variable=self.include_audio_var, value=False).pack(anchor="w")
        ttk.Label(audio_option_frame, text="※ OpenCV는 음성을 지원하지 않습니다",
                 foreground="gray").pack(anchor="w", padx=20)

        # 합치기 실행 버튼
        ttk.Button(parent, text="동영상 합치기", command=self.merge_videos,
                  style="Accent.TButton").pack(pady=20)

        # 진행 상태
        self.merge_progress_label = ttk.Label(parent, text="")
        self.merge_progress_label.pack()

        self.merge_progress = ttk.Progressbar(parent, mode='determinate')
        self.merge_progress.pack(fill="x", padx=10, pady=5)

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

    def select_video1(self):
        file_path = filedialog.askopenfilename(
            title="첫 번째 MP4 파일 선택",
            filetypes=[("MP4 파일", "*.mp4"), ("모든 파일", "*.*")]
        )

        if file_path:
            self.video1_path = file_path
            self.video1_label.config(text=Path(file_path).name)

            # 기본 저장 경로 설정
            if not self.merge_output_path:
                self.merge_output_path = str(Path(file_path).parent)

    def select_video2(self):
        file_path = filedialog.askopenfilename(
            title="두 번째 MP4 파일 선택",
            filetypes=[("MP4 파일", "*.mp4"), ("모든 파일", "*.*")]
        )

        if file_path:
            self.video2_path = file_path
            self.video2_label.config(text=Path(file_path).name)

    def select_merge_output(self):
        folder = filedialog.askdirectory(title="저장 폴더 선택")
        if folder:
            self.merge_output_path = folder
            self.merge_output_label.config(text=folder)

    def generate_output_filename(self):
        """두 파일명을 합쳐서 출력 파일명 생성, 중복 시 숫자 증가"""
        if not self.merge_output_path:
            messagebox.showerror("오류", "저장 경로를 선택하세요")
            return None

        # 두 동영상의 파일명 (확장자 제외)
        name1 = Path(self.video1_path).stem
        name2 = Path(self.video2_path).stem

        # 합친 기본 파일명
        base_name = f"{name1}_{name2}"
        output_file = os.path.join(self.merge_output_path, f"{base_name}.mp4")

        # 파일이 존재하면 숫자 증가
        counter = 1
        while os.path.exists(output_file):
            output_file = os.path.join(self.merge_output_path, f"{base_name}_{counter:03d}.mp4")
            counter += 1

        return output_file

    def merge_videos(self):
        if not self.video1_path or not self.video2_path:
            messagebox.showerror("오류", "두 개의 동영상 파일을 모두 선택하세요")
            return

        if not self.merge_output_path:
            messagebox.showerror("오류", "저장 경로를 선택하세요")
            return

        try:
            # 출력 파일명 생성
            output_file = self.generate_output_filename()
            if not output_file:
                return

            # 첫 번째 동영상 열기
            cap1 = cv2.VideoCapture(self.video1_path)
            cap2 = cv2.VideoCapture(self.video2_path)

            # 첫 번째 동영상 정보 가져오기
            fps1 = cap1.get(cv2.CAP_PROP_FPS)
            width1 = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
            height1 = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
            frames1 = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT))

            # 두 번째 동영상 정보 가져오기
            fps2 = cap2.get(cv2.CAP_PROP_FPS)
            width2 = int(cap2.get(cv2.CAP_PROP_FRAME_WIDTH))
            height2 = int(cap2.get(cv2.CAP_PROP_FRAME_HEIGHT))
            frames2 = int(cap2.get(cv2.CAP_PROP_FRAME_COUNT))

            # FPS와 해상도 통일 (첫 번째 동영상 기준)
            target_fps = fps1
            target_size = (width1, height1)

            # VideoWriter 생성
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_file, fourcc, target_fps, target_size)

            total_frames = frames1 + frames2
            processed_frames = 0

            # 첫 번째 동영상 처리
            self.merge_progress_label.config(text="첫 번째 동영상 처리 중...")
            while True:
                ret, frame = cap1.read()
                if not ret:
                    break

                # 해상도가 다르면 리사이즈
                if frame.shape[1] != width1 or frame.shape[0] != height1:
                    frame = cv2.resize(frame, target_size)

                out.write(frame)
                processed_frames += 1

                if processed_frames % 10 == 0:
                    self.merge_progress['value'] = (processed_frames / total_frames) * 100
                    self.merge_progress_label.config(text=f"진행 중: {processed_frames}/{total_frames} 프레임")
                    self.root.update_idletasks()

            cap1.release()

            # 두 번째 동영상 처리
            self.merge_progress_label.config(text="두 번째 동영상 처리 중...")

            # FPS가 다르면 프레임 간격 조정
            frame_ratio = fps2 / target_fps if fps2 > 0 else 1
            frame_count = 0

            while True:
                ret, frame = cap2.read()
                if not ret:
                    break

                # FPS 맞추기 위한 프레임 스킵
                if frame_ratio != 1:
                    if frame_count % max(1, int(frame_ratio)) != 0:
                        frame_count += 1
                        continue

                # 해상도가 다르면 리사이즈
                if frame.shape[1] != width1 or frame.shape[0] != height1:
                    frame = cv2.resize(frame, target_size)

                out.write(frame)
                processed_frames += 1
                frame_count += 1

                if processed_frames % 10 == 0:
                    self.merge_progress['value'] = (processed_frames / total_frames) * 100
                    self.merge_progress_label.config(text=f"진행 중: {processed_frames}/{total_frames} 프레임")
                    self.root.update_idletasks()

            cap2.release()
            out.release()

            self.merge_progress['value'] = 100
            self.merge_progress_label.config(text=f"완료! 저장 위치: {output_file}")
            messagebox.showinfo("완료", f"동영상 합치기가 완료되었습니다!\n\n저장 위치:\n{output_file}\n\n※ OpenCV는 음성을 지원하지 않아 동영상만 합쳐집니다.")

        except Exception as e:
            messagebox.showerror("오류", f"동영상 합치기 중 오류 발생:\n{str(e)}")
        finally:
            if 'cap1' in locals():
                cap1.release()
            if 'cap2' in locals():
                cap2.release()
            if 'out' in locals():
                out.release()


def main():
    root = tk.Tk()
    app = VideoFrameExtractor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
