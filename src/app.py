import re
import json
import time
import asyncio
import requests
import string
from config import *
from uuid import uuid4
from typing import List
import assemblyai as aai
from moviepy.editor import *
from datetime import datetime
from moviepy.video.fx.all import crop
from moviepy.audio.fx.all import volumex
from moviepy.config import change_settings
from moviepy.video.tools.subtitles import SubtitlesClip

change_settings({"IMAGEMAGICK_BINARY": get_imagemagick_path()})

class YouTube:
    def __init__(self, tts_path, images):
        self.tts_path = tts_path
        self.images = images


    
    def generate_subtitles(self, audio_path: str):
        """Generate visually enhanced word-highlighted subtitles with improved positioning and styling."""
        info("🎬 Starting enhanced subtitle generation process")
        
        try:
            # Configure AssemblyAI
            info("🔑 Configuring AssemblyAI")
            aai.settings.api_key = get_assemblyai_api_key()
            config = aai.TranscriptionConfig(
                speaker_labels=False,
                word_boost=[],
                format_text=True
            )
            transcriber = aai.Transcriber(config=config)
            
            # Get font configuration
            font = os.path.join(get_fonts_dir(), get_font())
            
            # Transcribe audio
            info("🎙️ Transcribing audio content")
            transcript = transcriber.transcribe(audio_path)
            
            # Enhanced word-level processing with improved timing
            info("📝 Processing word-level information with enhanced timing")
            wordlevel_info = []
            for word in transcript.words:
                # Add small padding between words for better timing
                word_data = {
                    "word": word.text.strip(),
                    "start": word.start / 1000.0,
                    "end": (word.end / 1000.0) + 0.05  # Add slight padding
                }
                wordlevel_info.append(word_data)
            
            # Save word-level JSON
            wordlevel_json = os.path.join(ROOT_DIR, ".mp", f"{uuid4()}_wordlevel.json")
            with open(wordlevel_json, 'w') as f:
                json.dump(wordlevel_info, f, indent=4)
            
            # Enhanced subtitle line generation with improved breaking
            info("📑 Generating optimized subtitle lines")
            subtitles = []
            line = []
            line_duration = 0
            optimal_chars = get_max_chars() * 0.7  # Target optimal line length
            
            for idx, word_data in enumerate(wordlevel_info):
                word = word_data["word"]
                start = word_data["start"]
                end = word_data["end"]
                
                line.append(word_data)
                line_duration += end - start
                current_line = " ".join(item["word"] for item in line)
                current_chars = len(current_line)
                
                # Enhanced line breaking logic
                should_break = False
                
                # Check various conditions for line breaks
                if current_chars >= optimal_chars:
                    should_break = True
                elif line_duration >= MAX_DURATION * 0.8:
                    should_break = True
                elif idx > 0:
                    gap = word_data['start'] - wordlevel_info[idx - 1]['end']
                    if gap > MAX_GAP * 0.5:
                        should_break = True
                
                # Natural break points
                if word.endswith(('.', '!', '?', ':', ';')):
                    should_break = True
                
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
            
            # Handle remaining words with grace
            if line:
                subtitle_line = {
                    "text": " ".join(item["word"] for item in line),
                    "start": line[0]["start"],
                    "end": line[-1]["end"],
                    "words": line
                }
                subtitles.append(subtitle_line)
            
            # Enhanced subtitle clip generation with improved positioning
            info("🎨 Generating visually enhanced subtitle clips")
            all_subtitle_clips = []
            
            for subtitle in subtitles:
                full_duration = subtitle['end'] - subtitle['start']
                word_clips = []
                xy_textclips_positions = []
                
                # Dynamic positioning calculation
                frame_width, frame_height = FRAME_SIZE
                base_y_pos = frame_height * 0.8  # Position subtitles lower
                x_margin = frame_width * 0.08  # Increased margin for better appearance
                word_spacing = 15  # Increased spacing between words
                
                x_pos = 0
                y_pos = base_y_pos
                current_line_width = 0
                max_line_width = frame_width - (2 * x_margin)
                
                # Enhanced word styling and positioning
                for wordJSON in subtitle['words']:
                    # Create temporary clip to measure size
                    temp_clip = TextClip(
                        wordJSON['word'],
                        font=font,
                        fontsize=get_font_size(),
                        color=get_text_color(),
                        stroke_color=get_stroke_color(),
                        stroke_width=get_stroke_width()
                    )
                    
                    word_width, word_height = temp_clip.size
                    
                    # Check if word needs to go to next line
                    if current_line_width + word_width > max_line_width:
                        x_pos = 0
                        y_pos += word_height * 1.2  # Add 20% extra spacing between lines
                        current_line_width = 0
                    
                    # Calculate centered position for current line
                    x_position = x_pos + x_margin
                    
                    # Store position information
                    xy_textclips_positions.append({
                        "x_pos": x_position,
                        "y_pos": y_pos,
                        "width": word_width,
                        "height": word_height,
                        "word": wordJSON['word'],
                        "start": wordJSON['start'],
                        "end": wordJSON['end'],
                        "duration": wordJSON['end'] - wordJSON['start']
                    })
                    
                    # Create and position the word clip
                    word_clip = TextClip(
                        wordJSON['word'],
                        font=font,
                        fontsize=get_font_size(),
                        color=get_text_color(),
                        stroke_color=get_stroke_color(),
                        stroke_width=get_stroke_width()
                    ).set_start(subtitle['start']).set_duration(full_duration)
                    
                    word_clip = word_clip.set_position((x_position, y_pos))
                    word_clips.append(word_clip)
                    
                    x_pos += word_width + word_spacing
                    current_line_width += word_width + word_spacing
                
                # Enhanced highlight effects with smooth transitions
                for highlight_word in xy_textclips_positions:
                    word_clip_highlight = TextClip(
                        highlight_word['word'],
                        font=font,
                        fontsize=get_font_size(),
                        color=get_text_color(),
                        bg_color=get_bg_color(),
                        stroke_color=get_stroke_color(),
                        stroke_width=get_stroke_width()
                    ).set_start(highlight_word['start']).set_duration(highlight_word['duration'])
                    
                    # Add fade effect for smooth transitions
                    word_clip_highlight = word_clip_highlight.crossfadein(0.1).crossfadeout(0.1)
                    
                    word_clip_highlight = word_clip_highlight.set_position(
                        (highlight_word['x_pos'], highlight_word['y_pos'])
                    )
                    word_clips.append(word_clip_highlight)
                
                all_subtitle_clips.extend(word_clips)
            
            info(f"✨ Successfully generated {len(all_subtitle_clips)} enhanced subtitle clips")
            return all_subtitle_clips
            
        except Exception as e:
            error(f"❌ Enhanced subtitle generation failed: {str(e)}")
            return []

    def combine(self) -> str:
        """Combine all elements into final video."""
        info("Starting to combine all elements into the final video")
        combined_image_path = os.path.join(ROOT_DIR, ".mp", f"{uuid4()}.mp4")
        threads = get_threads()
        
        tts_clip = AudioFileClip(self.tts_path)
        max_duration = tts_clip.duration
        req_dur = max_duration / len(self.images)
        
        clips = []
        tot_dur = 0
        while tot_dur < max_duration:
            for image_path in self.images:
                clip = ImageClip(image_path)
                clip.duration = req_dur
                clip = clip.set_fps(30)

                # Intelligent cropping for different aspect ratios
                aspect_ratio = 9/16  # Standard vertical video ratio
                if clip.w / clip.h < aspect_ratio:
                    clip = crop(
                        clip, 
                        width=clip.w, 
                        height=round(clip.w / aspect_ratio), 
                        x_center=clip.w / 2, 
                        y_center=clip.h / 2
                    )
                else:
                    clip = crop(
                        clip, 
                        width=round(aspect_ratio * clip.h), 
                        height=clip.h, 
                        x_center=clip.w / 2, 
                        y_center=clip.h / 2
                    )

                clip = clip.resize((1080, 1920))

                clips.append(clip)
                tot_dur += clip.duration

        final_clip = concatenate_videoclips(clips)
        final_clip = final_clip.set_fps(30)
        
        random_Music = choose_random_music()
        random_Music_clip = AudioFileClip(random_Music)
        random_Music_clip = random_Music_clip.fx(volumex, 0.1)
        random_Music_clip = random_Music_clip.set_duration(max_duration)
        
        word_highlighted_clips = self.generate_subtitles(self.tts_path)
        
        comp_audio = CompositeAudioClip([
            tts_clip,
            random_Music_clip
        ])

        final_clip = final_clip.set_audio(comp_audio)
        final_clip = final_clip.set_duration(tts_clip.duration)

        final_clip = CompositeVideoClip([
            final_clip
        ] + word_highlighted_clips)

        final_clip.write_videofile(combined_image_path, threads=threads)

        success(f"Video successfully created at: {combined_image_path}")
        return combined_image_path
