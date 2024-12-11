import os
import json
import random
from config import *
from uuid import uuid4
import assemblyai as aai
from moviepy.editor import *
from moviepy.video.fx.all import crop
from moviepy.audio.fx.all import volumex
from moviepy.config import change_settings
from moviepy.video.tools.subtitles import SubtitlesClip
from effect import zoom_in_effect, zoom_out_effect, rotate_effect

change_settings({"IMAGEMAGICK_BINARY": get_imagemagick_path()})

class SubtitlesGenerator:
    def __init__(self, tts_path, images):
        self.tts_path = tts_path
        self.images = images
        info(f"Initialized SubtitlesGenerator with {len(images)} images")
        assert_folder_structure()

    def choose_random_music(self):
        """Select random background music"""
        music_dir = get_music_dir()
        music_files = [f for f in os.listdir(music_dir) if f.endswith(('.mp3', '.wav'))]
        if not music_files:
            warning("No music files found in music directory")
            return None
        chosen_music = random.choice(music_files)
        info(f"Selected background music: {chosen_music}")
        return os.path.join(music_dir, chosen_music)
    
    def get_frame_size(self):
        """Get frame size based on dimension setting"""
        dimension = get_dimension()
        if dimension == "portrait":
            return (1080, 1920)
        elif dimension == "landscape":
            return (1920, 1080)
        else:  # square
            return (1080, 1080)

    def generate_subtitles(self, audio_path: str):
        """Generate visually enhanced word-highlighted subtitles"""
        info("Starting subtitle generation process")
        
        try:
            # Configure AssemblyAI
            aai.settings.api_key = get_assemblyai_api_key()
            transcriber = aai.Transcriber()
            
            # Get font configuration
            font = os.path.join(get_fonts_dir(), get_font())
            
            # Transcribe audio
            transcript = transcriber.transcribe(audio_path)
            
            # Process word-level information
            wordlevel_info = []
            for word in transcript.words:
                word_data = {
                    "word": word.text.strip(),
                    "start": word.start / 1000.0,
                    "end": (word.end / 1000.0) + 0.05
                }
                wordlevel_info.append(word_data)
            
            # Generate subtitle lines
            subtitles = []
            line = []
            line_duration = 0
            
            for idx, word_data in enumerate(wordlevel_info):
                line.append(word_data)
                line_duration = word_data["end"] - line[0]["start"]
                current_line = " ".join(item["word"] for item in line)
                
                should_break = (
                    len(current_line) >= get_max_chars() or
                    line_duration >= get_max_duration() or
                    (idx > 0 and word_data['start'] - wordlevel_info[idx-1]['end'] > get_max_gap())
                )
                
                if should_break and line:
                    subtitle_line = {
                        "text": " ".join(item["word"] for item in line),
                        "start": line[0]["start"],
                        "end": line[-1]["end"],
                        "words": line
                    }
                    subtitles.append(subtitle_line)
                    line = []
                    line_duration = 0
            
            # Handle remaining words
            if line:
                subtitles.append({
                    "text": " ".join(item["word"] for item in line),
                    "start": line[0]["start"],
                    "end": line[-1]["end"],
                    "words": line
                })
            
            # Generate subtitle clips
            frame_width, frame_height = self.get_frame_size()
            all_subtitle_clips = []
            
            for subtitle in subtitles:
                full_duration = subtitle['end'] - subtitle['start']
                word_clips = []
                x_pos = frame_width * 0.1  # 10% margin
                y_pos = frame_height * 0.8  # Position at 80% of height
                
                for word_data in subtitle['words']:
                    # Create word clip
                    word_clip = TextClip(
                        word_data['word'],
                        font=font,
                        fontsize=get_font_size(),
                        color=get_subtitle_color(),
                        stroke_color=get_stroke_color(),
                        stroke_width=get_stroke_width()
                    ).set_start(subtitle['start']).set_duration(full_duration)
                    
                    word_clip = word_clip.set_position((x_pos, y_pos))
                    word_clips.append(word_clip)
                    
                    # Add highlight effect if enabled
                    if get_highlight():
                        highlight_clip = TextClip(
                            word_data['word'],
                            font=font,
                            fontsize=get_font_size(),
                            color=get_subtitle_color(),
                            bg_color=get_highlight_color(),
                            stroke_color=get_stroke_color(),
                            stroke_width=get_stroke_width()
                        ).set_start(word_data['start']).set_duration(word_data['end'] - word_data['start'])
                        
                        highlight_clip = highlight_clip.set_position((x_pos, y_pos))
                        highlight_clip = highlight_clip.crossfadein(0.1).crossfadeout(0.1)
                        word_clips.append(highlight_clip)
                    
                    x_pos += word_clip.w + 15  # Add spacing between words
                
                all_subtitle_clips.extend(word_clips)
            
            return all_subtitle_clips
            
        except Exception as e:
            error(f"Subtitle generation failed: {str(e)}")
            return []

    def combine(self) -> str:
        """Combine all elements into final video"""
        info("Starting video combination process")
        combined_image_path = os.path.join(ROOT_DIR, ".mp", f"{uuid4()}.mp4")
        
        tts_clip = AudioFileClip(self.tts_path)
        max_duration = tts_clip.duration
        req_dur = max_duration / len(self.images)
        
        frame_width, frame_height = self.get_frame_size()
        clips = []
        tot_dur = 0
        
        while tot_dur < max_duration:
            for image_path in self.images:
                clip = ImageClip(image_path)
                clip = clip.set_duration(req_dur)
                clip = clip.set_fps(30)
                
                # Resize maintaining aspect ratio
                aspect_ratio = frame_width / frame_height
                if clip.w / clip.h > aspect_ratio:
                    new_width = int(clip.h * aspect_ratio)
                    clip = crop(clip, width=new_width, height=clip.h, x_center=clip.w/2)
                else:
                    new_height = int(clip.w / aspect_ratio)
                    clip = crop(clip, width=clip.w, height=new_height, y_center=clip.h/2)
                
                clip = clip.resize((frame_width, frame_height))
                clips.append(clip)
                tot_dur += clip.duration

        final_clip = concatenate_videoclips(clips)
        final_clip = final_clip.set_fps(30)
        
        # Add background music
        random_music = self.choose_random_music()
        if random_music:
            background_music = AudioFileClip(random_music)
            background_music = background_music.volumex(0.1)
            background_music = background_music.set_duration(max_duration)
            
            # Generate subtitles if enabled
            subtitle_clips = []
            if get_subtitles():
                subtitle_clips = self.generate_subtitles(self.tts_path)
            
            # Combine audio
            final_audio = CompositeAudioClip([tts_clip, background_music])
            final_clip = final_clip.set_audio(final_audio)
            final_clip = final_clip.set_duration(max_duration)
            
            # Add subtitles if available
            if subtitle_clips:
                final_clip = CompositeVideoClip([final_clip] + subtitle_clips)
            
            # Write final video
            final_clip.write_videofile(
                combined_image_path,
                threads=get_threads(),
                fps=30,
                codec='libx264',
                audio_codec='aac'
            )
            
            success(f"Video successfully created at: {combined_image_path}")
            return combined_image_path
        else:
            error("No background music available")
            return None
