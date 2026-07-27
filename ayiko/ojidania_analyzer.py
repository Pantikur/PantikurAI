#!/usr/bin/env python3
"""
Ayiko AI — Image Analyzer (Ojidania)
Zone: Photo study, relief, light, clothing, mimicry analysis

Functions:
- Body relief and muscle analysis
- Clothing draping and contours
- Light and shadow analysis
- Gloss effects (eyes, sweat, water)
- Depth layers (foreground/background)
- Composition layers
- Facial mimicry and expressions
- Generation based on learned patterns
"""

import os
import json
import math
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional
from datetime import datetime

try:
    from PIL import Image as PILImage
    from PIL import ImageDraw, ImageFilter, ImageEnhance
    import numpy as np
except ImportError:
    print("WARNING: PIL and numpy not installed. Install: pip install Pillow numpy")
    PILImage = None
    ImageDraw = None
    ImageFilter = None
    ImageEnhance = None
    np = None


class OjidaniaAnalyzer:
    """Image analyzer for Ayiko to learn from photographs"""
    
    def __init__(self, ojidania_dir: str = "ayiko/ojidania", output_dir: str = "data/ayiko/ojidania_analysis"):
        self.ojidania_dir = Path(ojidania_dir)
        self.ojidania_dir.mkdir(parents=True, exist_ok=True)
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Knowledge base from analysis
        self.knowledge = {
            "body_relief": {},
            "clothing_draping": {},
            "lighting_patterns": {},
            "gloss_effects": {},
            "depth_layers": {},
            "facial_mimicry": {},
            "muscle_structure": {},
            "texture_analysis": {}
        }
        
        self.training_data = []
        self.image_count = 0
        
    def analyze_image(self, image_path: str) -> Dict:
        """
        Full image analysis
        
        Args:
            image_path: Path to image
        
        Returns:
            Dict with analysis results
        """
        if PILImage is None:
            return {"error": "PIL not installed"}
        
        try:
            img = PILImage.open(image_path)
            img_array = np.array(img) if np is not None else None
            
            analysis = {
                "filename": Path(image_path).name,
                "timestamp": datetime.now().isoformat(),
                "basic_info": self._analyze_basic_info(img),
                "body_relief": self._analyze_body_relief(img_array, img.size) if img_array is not None else {},
                "clothing_analysis": self._analyze_clothing_draping(img_array, img.size) if img_array is not None else {},
                "lighting": self._analyze_lighting(img_array, img.size) if img_array is not None else {},
                "gloss_effects": self._analyze_gloss_effects(img_array, img.size) if img_array is not None else {},
                "depth_composition": self._analyze_depth_layers(img_array, img.size) if img_array is not None else {},
                "facial_analysis": self._analyze_facial_mimicry(img_array, img.size) if img_array is not None else {},
                "muscle_structure": self._analyze_muscle_structure(img_array, img.size) if img_array is not None else {},
                "texture_analysis": self._analyze_textures(img_array, img.size) if img_array is not None else {},
                "overall_quality": self._assess_quality(img, img_array)
            }
            
            # Save analysis
            self._save_analysis(analysis)
            
            # Update knowledge base
            self._update_knowledge(analysis)
            
            self.image_count += 1
            return analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_basic_info(self, img: PILImage.Image) -> Dict:
        """Basic image information"""
        return {
            "size": img.size,
            "mode": img.mode,
            "format": img.format,
            "width": img.width,
            "height": img.height,
            "aspect_ratio": img.width / img.height if img.height > 0 else 0
        }
    
    def _analyze_body_relief(self, img_array: Any, size: Tuple[int, int]) -> Dict:
        """Body relief analysis"""
        if np is None:
            return {}
        
        # Convert to grayscale for relief analysis
        gray = np.mean(img_array[:, :, :3], axis=2) if img_array.shape[2] >= 3 else img_array
        
        # Calculate gradients (brightness changes = relief)
        dy, dx = np.gradient(gray)
        magnitude = np.sqrt(dx**2 + dy**2)
        
        # Analyze body zones by location
        height, width = gray.shape
        head_zone = gray[int(height*0.1):int(height*0.3), int(width*0.3):int(width*0.7)]
        torso_zone = gray[int(height*0.3):int(height*0.6), int(width*0.25):int(width*0.75)]
        limbs_zone = gray[int(height*0.6):int(height*0.9), :]
        
        return {
            "relief_intensity": float(np.mean(magnitude)),
            "body_zones": {
                "head": {
                    "avg_brightness": float(np.mean(head_zone)) if head_zone.size > 0 else 0,
                    "contrast": float(np.std(head_zone)) if head_zone.size > 0 else 0,
                    "detail_level": "high" if np.std(head_zone) > 30 else "medium" if np.std(head_zone) > 15 else "low"
                },
                "torso": {
                    "avg_brightness": float(np.mean(torso_zone)) if torso_zone.size > 0 else 0,
                    "curvature": self._estimate_curvature(torso_zone),
                    "fabric_tension": self._estimate_fabric_tension(torso_zone)
                },
                "limbs": {
                    "avg_brightness": float(np.mean(limbs_zone)) if limbs_zone.size > 0 else 0,
                    "muscle_definition": self._estimate_muscle_definition(limbs_zone)
                }
            },
            "surface_texture": {
                "smoothness": float(1.0 / (1.0 + np.std(magnitude))),
                "roughness": float(np.std(magnitude) / (np.mean(magnitude) + 1e-6))
            }
        }
    
    def _analyze_clothing_draping(self, img_array: Any, size: Tuple[int, int]) -> Dict:
        """Clothing and body contour analysis"""
        if np is None:
            return {}
        
        gray = np.mean(img_array[:, :, :3], axis=2) if img_array.shape[2] >= 3 else img_array
        height, width = gray.shape
        
        # Analyze folds and tension
        dy, dx = np.gradient(gray)
        
        # Clothing zones
        upper_body = gray[int(height*0.25):int(height*0.6), int(width*0.2):int(width*0.8)]
        
        # Calculate fabric tension
        tension_map = np.abs(dx) + np.abs(dy)
        tension_zones = {
            "shoulders": float(np.mean(tension_map[int(height*0.25):int(height*0.35), int(width*0.3):int(width*0.4)])),
            "chest": float(np.mean(tension_map[int(height*0.35):int(height*0.5), int(width*0.35):int(width*0.65)])),
            "waist": float(np.mean(tension_map[int(height*0.5):int(height*0.6), int(width*0.35):int(width*0.65)])),
            "hips": float(np.mean(tension_map[int(height*0.6):int(height*0.7), int(width*0.3):int(width*0.7)]))
        }
        
        # Classify drapery type
        drapery_type = self._classify_drapery(tension_zones)
        
        return {
            "drapery_type": drapery_type,
            "fabric_tension": tension_zones,
            "wrinkle_density": float(np.sum(tension_map > 20) / tension_map.size),
            "body_contours_visible": self._estimate_body_contours(upper_body),
            "fit_type": self._classify_fit(tension_zones)
        }
    
    def _analyze_lighting(self, img_array: Any, size: Tuple[int, int]) -> Dict:
        """Light and shadow analysis"""
        if np is None:
            return {}
        
        # Brightness analysis by zones
        height, width = img_array.shape[:2]
        top = img_array[:height//3, :]
        middle = img_array[height//3:2*height//3, :]
        bottom = img_array[2*height//3:, :]
        
        brightness_zones = {
            "top": float(np.mean(top[:, :, :3])),
            "middle": float(np.mean(middle[:, :, :3])),
            "bottom": float(np.mean(bottom[:, :, :3]))
        }
        
        # Determine light direction
        left_side = img_array[:, :width//2, :3]
        right_side = img_array[:, width//2:, :3]
        
        lighting_direction = self._determine_light_direction(left_side, right_side)
        
        # Contrast
        contrast = float(np.std(img_array[:, :, :3].flatten()) / (np.mean(img_array[:, :, :3].flatten()) + 1e-6))
        
        # Shadow softness
        shadow_softness = self._analyze_shadow_softness(img_array)
        
        return {
            "brightness_zones": brightness_zones,
            "light_direction": lighting_direction,
            "contrast": contrast,
            "shadow_softness": shadow_softness,
            "lighting_quality": self._classify_lighting(contrast, shadow_softness),
            "highlight_areas": self._find_highlights(img_array)
        }
    
    def _analyze_gloss_effects(self, img_array: Any, size: Tuple[int, int]) -> Dict:
        """Gloss analysis (eyes, sweat, water)"""
        if np is None:
            return {}
        
        # Find bright areas (blazing highlights)
        rgb_mean = np.mean(img_array[:, :, :3], axis=2)
        bright_areas = rgb_mean > 220
        
        # Specular highlights analysis
        specular_intensity = float(np.sum(bright_areas) / bright_areas.size)
        
        # Classify gloss type
        gloss_type = self._classify_gloss_type(img_array, bright_areas)
        
        # Reflection analysis
        reflection_quality = self._analyze_reflections(img_array, bright_areas)
        
        return {
            "specular_intensity": specular_intensity,
            "gloss_type": gloss_type,
            "reflection_quality": reflection_quality,
            "wet_effect": self._detect_wet_surfaces(img_array),
            "eye_glint": self._detect_eye_glint(img_array)
        }
    
    def _analyze_depth_layers(self, img_array: Any, size: Tuple[int, int]) -> Dict:
        """Depth layers and composition analysis"""
        if np is None:
            return {}
        
        height, width = img_array.shape[:2]
        
        # Separate into layers by brightness and sharpness
        gray = np.mean(img_array[:, :, :3], axis=2)
        
        # Foreground (bottom part, usually brighter)
        foreground = gray[int(height*0.6):, :]
        
        # Midground
        midground = gray[int(height*0.3):int(height*0.6), :]
        
        # Background (top part, usually darker)
        background = gray[:int(height*0.3), :]
        
        # Layer contrast
        layer_contrast = {
            "foreground_bg": float(np.std(foreground)),
            "midground_bg": float(np.std(midground)),
            "background_bg": float(np.std(background))
        }
        
        # Layer sharpness (depth of field)
        sharpness = {
            "foreground": float(np.std(np.gradient(foreground))),
            "midground": float(np.std(np.gradient(midground))),
            "background": float(np.std(np.gradient(background)))
        }
        
        # Scene depth score
        depth_score = self._calculate_depth_score(sharpness)
        
        return {
            "layers": {
                "foreground": {
                    "brightness": float(np.mean(foreground)),
                    "sharpness": sharpness["foreground"],
                    "content_density": float(np.sum(foreground > 50) / foreground.size)
                },
                "midground": {
                    "brightness": float(np.mean(midground)),
                    "sharpness": sharpness["midground"],
                    "content_density": float(np.sum(midground > 50) / midground.size)
                },
                "background": {
                    "brightness": float(np.mean(background)),
                    "sharpness": sharpness["background"],
                    "content_density": float(np.sum(background > 50) / background.size)
                }
            },
            "layer_contrast": layer_contrast,
            "depth_score": depth_score,
            "composition_type": self._classify_composition(sharpness, layer_contrast)
        }
    
    def _analyze_facial_mimicry(self, img_array: Any, size: Tuple[int, int]) -> Dict:
        """Facial mimicry and expressions analysis"""
        if np is None:
            return {}
        
        height, width = img_array.shape[:2]
        
        # Face zone (upper third, center)
        face_zone = img_array[int(height*0.15):int(height*0.45), int(width*0.3):int(width*0.7)]
        
        if face_zone.size == 0:
            return {"error": "Face zone not detected"}
        
        # Face contrast analysis
        face_gray = np.mean(face_zone[:, :, :3], axis=2) if face_zone.shape[2] >= 3 else face_zone
        
        # Face shadows (determine expression)
        shadows = face_gray < np.mean(face_gray) * 0.6
        highlight_areas = face_gray > np.mean(face_gray) * 1.4
        
        # Wrinkles and lines analysis
        edge_map = np.abs(np.gradient(face_gray))
        wrinkle_density = float(np.sum(edge_map > 30) / edge_map.size)
        
        # Emotion classification (simplified by shadows)
        emotion = self._classify_emotion(face_gray, shadows, highlight_areas)
        
        return {
            "face_detected": True,
            "face_brightness": float(np.mean(face_gray)),
            "shadow_ratio": float(np.sum(shadows) / shadows.size),
            "highlight_ratio": float(np.sum(highlight_areas) / highlight_areas.size),
            "wrinkle_density": wrinkle_density,
            "emotion": emotion,
            "facial_tension": self._estimate_facial_tension(face_gray)
        }
    
    def _analyze_muscle_structure(self, img_array: Any, size: Tuple[int, int]) -> Dict:
        """Muscle structure analysis"""
        if np is None:
            return {}
        
        gray = np.mean(img_array[:, :, :3], axis=2) if img_array.shape[2] >= 3 else img_array
        height, width = gray.shape
        
        # Gradients show muscle contours
        dy, dx = np.gradient(gray)
        gradient_magnitude = np.sqrt(dx**2 + dy**2)
        
        # Muscle zones
        chest_zone = gray[int(height*0.3):int(height*0.5), int(width*0.3):int(width*0.7)]
        arm_zone = gray[int(height*0.3):int(height*0.6), :]
        leg_zone = gray[int(height*0.6):int(height*0.9), :]
        
        muscle_definition = {
            "chest": float(np.std(gradient_magnitude[int(height*0.3):int(height*0.5), int(width*0.3):int(width*0.7)])),
            "arms": float(np.std(gradient_magnitude[int(height*0.3):int(height*0.6), :])),
            "legs": float(np.std(gradient_magnitude[int(height*0.6):int(height*0.9), :]))
        }
        
        # Classify body type
        body_type = self._classify_body_type(muscle_definition)
        
        return {
            "muscle_definition": muscle_definition,
            "overall_definition_score": float(np.mean(list(muscle_definition.values()))),
            "body_type": body_type,
            "muscle_contours_visible": self._estimate_muscle_visibility(gradient_magnitude)
        }
    
    def _analyze_textures(self, img_array: Any, size: Tuple[int, int]) -> Dict:
        """Texture analysis"""
        if np is None:
            return {}
        
        gray = np.mean(img_array[:, :, :3], axis=2) if img_array.shape[2] >= 3 else img_array
        
        # Pixel variability analysis (texture)
        texture_variability = float(np.std(gray))
        
        # Texture classification
        if texture_variability < 20:
            texture_type = "smooth"
        elif texture_variability < 50:
            texture_type = "fine"
        elif texture_variability < 100:
            texture_type = "medium"
        else:
            texture_type = "rough"
        
        return {
            "variability": texture_variability,
            "texture_type": texture_type,
            "detail_level": "high" if texture_variability > 80 else "medium" if texture_variability > 40 else "low"
        }
    
    def _assess_quality(self, img: PILImage.Image, img_array: Any) -> Dict:
        """Image quality assessment"""
        quality = {
            "resolution": "high" if img.width > 1000 and img.height > 1000 else "medium" if img.width > 500 else "low",
            "sharpness": "good",
            "lighting": "balanced"
        }
        
        if img_array is not None and np is not None:
            # Sharpness estimation via gradient variance
            gray = np.mean(img_array[:, :, :3], axis=2) if img_array.shape[2] >= 3 else img_array
            dy, dx = np.gradient(gray)
            sharpness_score = float(np.mean(np.sqrt(dx**2 + dy**2)))
            quality["sharpness_score"] = sharpness_score
            quality["sharpness"] = "excellent" if sharpness_score > 50 else "good" if sharpness_score > 20 else "poor"
        
        return quality
    
    def _save_analysis(self, analysis: Dict):
        """Save analysis to file"""
        filename = Path(analysis["filename"]).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"{filename}_{timestamp}_analysis.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    def _update_knowledge(self, analysis: Dict):
        """Update knowledge base from analysis"""
        if "body_relief" in analysis and analysis["body_relief"]:
            self.knowledge["body_relief"][analysis["filename"]] = analysis["body_relief"]
        
        if "clothing_analysis" in analysis and analysis["clothing_analysis"]:
            self.knowledge["clothing_draping"][analysis["filename"]] = analysis["clothing_analysis"]
        
        if "lighting" in analysis and analysis["lighting"]:
            self.knowledge["lighting_patterns"][analysis["filename"]] = analysis["lighting"]
        
        if "gloss_effects" in analysis and analysis["gloss_effects"]:
            self.knowledge["gloss_effects"][analysis["filename"]] = analysis["gloss_effects"]
        
        if "depth_composition" in analysis and analysis["depth_composition"]:
            self.knowledge["depth_layers"][analysis["filename"]] = analysis["depth_composition"]
        
        if "facial_analysis" in analysis and analysis["facial_analysis"]:
            self.knowledge["facial_mimicry"][analysis["filename"]] = analysis["facial_analysis"]
        
        if "muscle_structure" in analysis and analysis["muscle_structure"]:
            self.knowledge["muscle_structure"][analysis["filename"]] = analysis["muscle_structure"]
    
    def _save_training_data(self):
        """Save collected training data"""
        training_file = self.output_dir / "training_data.json"
        with open(training_file, "w", encoding="utf-8") as f:
            json.dump(self.knowledge, f, ensure_ascii=False, indent=2)
    
    # === Helper methods ===
    
    def _estimate_curvature(self, zone: Any) -> str:
        """Estimate surface curvature"""
        if zone.size == 0:
            return "flat"
        std = np.std(zone)
        if std > 50:
            return "high_curvature"
        elif std > 25:
            return "medium_curvature"
        return "low_curvature"
    
    def _estimate_fabric_tension(self, zone: Any) -> str:
        """Estimate fabric tension"""
        if zone.size == 0:
            return "loose"
        contrast = np.std(zone) / (np.mean(zone) + 1e-6)
        if contrast > 0.3:
            return "tight"
        elif contrast > 0.15:
            return "medium"
        return "loose"
    
    def _estimate_muscle_definition(self, zone: Any) -> str:
        """Estimate muscle definition"""
        if zone.size == 0:
            return "none"
        std = np.std(zone)
        if std > 40:
            return "high"
        elif std > 20:
            return "medium"
        return "low"
    
    def _classify_drapery(self, tension_zones: Dict) -> str:
        """Classify drapery type"""
        avg_tension = np.mean(list(tension_zones.values()))
        if avg_tension > 50:
            return "tight_fitting"
        elif avg_tension > 25:
            return "fitted"
        return "loose"
    
    def _classify_fit(self, tension_zones: Dict) -> str:
        """Classify clothing fit"""
        chest = tension_zones.get("chest", 0)
        waist = tension_zones.get("waist", 0)
        
        if chest > 40 and waist < 20:
            return "athletic"
        elif chest > 30:
            return "fitted"
        return "loose"
    
    def _determine_light_direction(self, left: Any, right: Any) -> str:
        """Determine light direction"""
        left_mean = np.mean(left)
        right_mean = np.mean(right)
        
        if left_mean > right_mean * 1.1:
            return "left"
        elif right_mean > left_mean * 1.1:
            return "right"
        elif left_mean > right_mean:
            return "front-left"
        else:
            return "front-right"
    
    def _analyze_shadow_softness(self, img_array: Any) -> str:
        """Analyze shadow softness"""
        gray = np.mean(img_array[:, :, :3], axis=2)
        dy, dx = np.gradient(gray)
        edge_width = float(np.mean(np.sqrt(dx**2 + dy**2)))
        
        if edge_width > 40:
            return "hard"
        elif edge_width > 20:
            return "soft"
        return "very_soft"
    
    def _classify_lighting(self, contrast: float, shadow_softness: str) -> str:
        """Classify lighting quality"""
        if contrast > 0.5:
            return "dramatic"
        elif contrast > 0.3:
            return "balanced"
        return "flat"
    
    def _find_highlights(self, img_array: Any) -> List[str]:
        """Find highlight areas"""
        rgb_mean = np.mean(img_array[:, :, :3], axis=2)
        bright = rgb_mean > 200
        
        height, width = img_array.shape[:2]
        top = np.sum(bright[:height//3, :])
        middle = np.sum(bright[height//3:2*height//3, :])
        bottom = np.sum(bright[2*height//3:, :])
        
        highlights = []
        if top > middle and top > bottom:
            highlights.append("top")
        if middle > top and middle > bottom:
            highlights.append("middle")
        if bottom > top and bottom > middle:
            highlights.append("bottom")
        
        return highlights if highlights else ["center"]
    
    def _classify_gloss_type(self, img_array: Any, bright_areas: Any) -> str:
        """Classify gloss type"""
        if np.sum(bright_areas) / bright_areas.size < 0.01:
            return "matte"
        
        bright_coords = np.argwhere(bright_areas)
        if len(bright_coords) == 0:
            return "matte"
        
        if np.std(bright_coords[:, 0]) < 10 and np.std(bright_coords[:, 1]) < 10:
            return "specular_point"
        
        return "diffuse_gloss"
    
    def _analyze_reflections(self, img_array: Any, bright_areas: Any) -> Dict:
        """Analyze reflections"""
        return {
            "intensity": float(np.sum(bright_areas) / bright_areas.size),
            "clarity": "sharp" if np.sum(bright_areas) < bright_areas.size * 0.05 else "soft"
        }
    
    def _detect_wet_surfaces(self, img_array: Any) -> bool:
        """Detect wet surfaces"""
        rgb_mean = np.mean(img_array[:, :, :3], axis=2)
        bright_areas = rgb_mean > 220
        
        if np.sum(bright_areas) / bright_areas.size > 0.05:
            return True
        return False
    
    def _detect_eye_glint(self, img_array: Any) -> bool:
        """Detect eye glint"""
        height, width = img_array.shape[:2]
        
        eye_zone = img_array[int(height*0.2):int(height*0.35), int(width*0.35):int(width*0.65)]
        
        if eye_zone.size == 0:
            return False
        
        rgb_mean = np.mean(eye_zone[:, :, :3], axis=2)
        bright = rgb_mean > 200
        
        return np.sum(bright) > 5 and np.sum(bright) < eye_zone.size * 0.1
    
    def _classify_composition(self, sharpness: Dict, contrast: Dict) -> str:
        """Classify composition type"""
        fg = sharpness.get("foreground", 0)
        bg = sharpness.get("background", 0)
        
        if fg > bg * 1.5:
            return "shallow_depth"
        elif abs(fg - bg) < 10:
            return "deep_focus"
        return "selective_focus"
    
    def _classify_emotion(self, face_gray: Any, shadows: Any, highlights: Any) -> str:
        """Simplified emotion classification"""
        shadow_ratio = np.sum(shadows) / shadows.size
        highlight_ratio = np.sum(highlights) / highlights.size
        
        if shadow_ratio > 0.4:
            return "serious"
        elif highlight_ratio > 0.2:
            return "happy"
        elif shadow_ratio > 0.3 and highlight_ratio < 0.1:
            return "neutral"
        return "unknown"
    
    def _estimate_facial_tension(self, face_gray: Any) -> str:
        """Estimate facial muscle tension"""
        if face_gray.size == 0:
            return "relaxed"
        gradient = np.abs(np.gradient(face_gray))
        if np.mean(gradient) > 30:
            return "tense"
        return "relaxed"
    
    def _estimate_body_contours(self, zone: Any) -> bool:
        """Determine body contour visibility"""
        if zone.size == 0:
            return False
        return np.std(zone) > 30
    
    def _classify_body_type(self, muscle_def: Dict) -> str:
        """Classify body type"""
        chest = muscle_def.get("chest", 0)
        arms = muscle_def.get("arms", 0)
        
        if chest > 40 and arms > 40:
            return "athletic"
        elif chest > 30:
            return "muscular"
        return "slim"
    
    def _estimate_muscle_visibility(self, gradient_magnitude: Any) -> bool:
        """Determine muscle visibility"""
        return float(np.mean(gradient_magnitude)) > 25
    
    def _calculate_depth_score(self, sharpness: Dict) -> float:
        """Calculate scene depth score"""
        fg = sharpness.get("foreground", 0)
        bg = sharpness.get("background", 0)
        
        if bg == 0:
            return 1.0
        
        return min(1.0, fg / (bg + 1e-6))
    
    def batch_analyze(self, directory: str = "ayiko/ojidania") -> List[Dict]:
        """Batch analyze all images in directory"""
        ojidania_path = Path(directory)
        if not ojidania_path.exists():
            return []
        
        image_files = list(ojidania_path.glob("*.jpg")) + \
                      list(ojidania_path.glob("*.jpeg")) + \
                      list(ojidania_path.glob("*.png"))
        
        results = []
        for img_file in image_files:
            print(f"Analyzing: {img_file.name}")
            result = self.analyze_image(str(img_file))
            results.append(result)
        
        self._save_training_data()
        return results
    
    def get_stats(self) -> Dict:
        """Get analysis statistics"""
        return {
            "images_analyzed": self.image_count,
            "knowledge_sections": {
                "body_relief": len(self.knowledge["body_relief"]),
                "clothing_draping": len(self.knowledge["clothing_draping"]),
                "lighting_patterns": len(self.knowledge["lighting_patterns"]),
                "gloss_effects": len(self.knowledge["gloss_effects"]),
                "depth_layers": len(self.knowledge["depth_layers"]),
                "facial_mimicry": len(self.knowledge["facial_mimicry"]),
                "muscle_structure": len(self.knowledge["muscle_structure"])
            }
        }


# API for FastAPI integration
def create_analyzer():
    """Create analyzer instance"""
    return OjidaniaAnalyzer()


if __name__ == "__main__":
    import sys
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = open(1, 'w', encoding='utf-8', closefd=False)
    
    analyzer = OjidaniaAnalyzer()
    
    print("Testing Ojidania Image Analyzer...")
    print("Place images in ayiko/ojidania/ folder and run batch_analyze()")
    
    # Example usage:
    # results = analyzer.batch_analyze("ayiko/ojidania")
    # print(f"Analyzed {len(results)} images")
    # print(analyzer.get_stats())
