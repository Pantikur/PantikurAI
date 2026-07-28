#!/usr/bin/env python3
"""
Ayiko AI - Image Analyzer (Ojidania)
Zone: Photo study, relief, light, clothing, mimicry analysis
"""

import os
import json
import math
from pathlib import Path
from typing import List, Dict, Tuple, Any
from datetime import datetime

# Импорт с обработкой ошибок
try:
    from PIL import Image as PILImage
    from PIL import ImageDraw, ImageFilter, ImageEnhance
    import numpy as np
except ImportError as e:
    print(f"WARNING: Missing dependencies: {e}")
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
            "texture_analysis": {},
            "objects": {},
            "clothing_items": {},
            "accessories": {},
            "3d_structure": {}
        }
        
        self.image_count = 0
        
    def analyze_image(self, image_path: str) -> Dict:
        """Full image analysis"""
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
                "objects_detected": self._detect_objects(img_array, img.size) if img_array is not None else {},
                "clothing_items": self._detect_clothing_items(img_array, img.size) if img_array is not None else {},
                "accessories_detected": self._detect_accessories(img_array, img.size) if img_array is not None else {},
                "3d_structure": self._analyze_3d_structure(img_array, img.size) if img_array is not None else {},
                "overall_quality": self._assess_quality(img, img_array)
            }
            
            self._save_analysis(analysis)
            self._update_knowledge(analysis)
            self.image_count += 1
            return analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_basic_info(self, img: Any) -> Dict:
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
        
        gray = np.mean(img_array[:, :, :3], axis=2) if img_array.shape[2] >= 3 else img_array
        dy, dx = np.gradient(gray)
        magnitude = np.sqrt(dx**2 + dy**2)
        
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
        
        dy, dx = np.gradient(gray)
        upper_body = gray[int(height*0.25):int(height*0.6), int(width*0.2):int(width*0.8)]
        
        tension_map = np.abs(dx) + np.abs(dy)
        tension_zones = {
            "shoulders": float(np.mean(tension_map[int(height*0.25):int(height*0.35), int(width*0.3):int(width*0.4)])),
            "chest": float(np.mean(tension_map[int(height*0.35):int(height*0.5), int(width*0.35):int(width*0.65)])),
            "waist": float(np.mean(tension_map[int(height*0.5):int(height*0.6), int(width*0.35):int(width*0.65)])),
            "hips": float(np.mean(tension_map[int(height*0.6):int(height*0.7), int(width*0.3):int(width*0.7)]))
        }
        
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
        
        height, width = img_array.shape[:2]
        top = img_array[:height//3, :]
        middle = img_array[height//3:2*height//3, :]
        bottom = img_array[2*height//3:, :]
        
        brightness_zones = {
            "top": float(np.mean(top[:, :, :3])),
            "middle": float(np.mean(middle[:, :, :3])),
            "bottom": float(np.mean(bottom[:, :, :3]))
        }
        
        left_side = img_array[:, :width//2, :3]
        right_side = img_array[:, width//2:, :3]
        
        lighting_direction = self._determine_light_direction(left_side, right_side)
        contrast = float(np.std(img_array[:, :, :3].flatten()) / (np.mean(img_array[:, :, :3].flatten()) + 1e-6))
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
        
        rgb_mean = np.mean(img_array[:, :, :3], axis=2)
        bright_areas = rgb_mean > 220
        specular_intensity = float(np.sum(bright_areas) / bright_areas.size)
        
        gloss_type = self._classify_gloss_type(img_array, bright_areas)
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
        gray = np.mean(img_array[:, :, :3], axis=2)
        
        foreground = gray[int(height*0.6):, :]
        midground = gray[int(height*0.3):int(height*0.6), :]
        background = gray[:int(height*0.3), :]
        
        layer_contrast = {
            "foreground_bg": float(np.std(foreground)),
            "midground_bg": float(np.std(midground)),
            "background_bg": float(np.std(background))
        }
        
        sharpness = {
            "foreground": float(np.std(np.gradient(foreground))),
            "midground": float(np.std(np.gradient(midground))),
            "background": float(np.std(np.gradient(background)))
        }
        
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
        face_zone = img_array[int(height*0.15):int(height*0.45), int(width*0.3):int(width*0.7)]
        
        if face_zone.size == 0:
            return {"error": "Face zone not detected"}
        
        face_gray = np.mean(face_zone[:, :, :3], axis=2) if face_zone.shape[2] >= 3 else face_zone
        shadows = face_gray < np.mean(face_gray) * 0.6
        highlight_areas = face_gray > np.mean(face_gray) * 1.4
        
        edge_map = np.abs(np.gradient(face_gray))
        wrinkle_density = float(np.sum(edge_map > 30) / edge_map.size)
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
        
        dy, dx = np.gradient(gray)
        gradient_magnitude = np.sqrt(dx**2 + dy**2)
        
        muscle_definition = {
            "chest": float(np.std(gradient_magnitude[int(height*0.3):int(height*0.5), int(width*0.3):int(width*0.7)])),
            "arms": float(np.std(gradient_magnitude[int(height*0.3):int(height*0.6), :])),
            "legs": float(np.std(gradient_magnitude[int(height*0.6):int(height*0.9), :]))
        }
        
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
        texture_variability = float(np.std(gray))
        
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
    
    def _assess_quality(self, img: Any, img_array: Any) -> Dict:
        """Image quality assessment"""
        quality = {
            "resolution": "high" if img.width > 1000 and img.height > 1000 else "medium" if img.width > 500 else "low",
            "sharpness": "good",
            "lighting": "balanced"
        }
        
        if img_array is not None and np is not None:
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
        
        if "objects_detected" in analysis and analysis["objects_detected"]:
            self.knowledge["objects"][analysis["filename"]] = analysis["objects_detected"]
        
        if "clothing_items" in analysis and analysis["clothing_items"]:
            self.knowledge["clothing_items"][analysis["filename"]] = analysis["clothing_items"]
        
        if "accessories_detected" in analysis and analysis["accessories_detected"]:
            self.knowledge["accessories"][analysis["filename"]] = analysis["accessories_detected"]
        
        if "3d_structure" in analysis and analysis["3d_structure"]:
            self.knowledge["3d_structure"][analysis["filename"]] = analysis["3d_structure"]
    
    def _save_training_data(self):
        """Save collected training data"""
        training_file = self.output_dir / "training_data.json"
        with open(training_file, "w", encoding="utf-8") as f:
            json.dump(self.knowledge, f, ensure_ascii=False, indent=2)
    
    # === Object Detection ===
    
    def _detect_objects(self, img_array: Any, size: Tuple[int, int]) -> Dict:
        """Detect and classify objects in image"""
        if np is None:
            return {}
        
        height, width = img_array.shape[:2]
        gray = np.mean(img_array[:, :, :3], axis=2) if img_array.shape[2] >= 3 else img_array
        
        # Detect edges and contours
        dy, dx = np.gradient(gray)
        edge_map = np.sqrt(dx**2 + dy**2)
        
        # Find object regions
        objects = []
        
        # Analyze by zones
        zones = {
            "head": gray[int(height*0.05):int(height*0.35), int(width*0.3):int(width*0.7)],
            "torso": gray[int(height*0.35):int(height*0.65), int(width*0.2):int(width*0.8)],
            "arms": [
                gray[int(height*0.35):int(height*0.65), int(width*0.05):int(width*0.2)],
                gray[int(height*0.35):int(height*0.65), int(width*0.8):int(width*0.95)]
            ],
            "legs": [
                gray[int(height*0.65):int(height*0.95), int(width*0.3):int(width*0.45)],
                gray[int(height*0.65):int(height*0.95), int(width*0.55):int(width*0.7)]
            ]
        }
        
        # Classify objects based on texture and shape
        for zone_name, zone_data in zones.items():
            if isinstance(zone_data, list):
                for i, zone in enumerate(zone_data):
                    obj = self._classify_zone_object(zone, zone_name, f"left" if i == 0 else "right")
                    if obj:
                        objects.append(obj)
            else:
                obj = self._classify_zone_object(zone_data, zone_name, "center")
                if obj:
                    objects.append(obj)
        
        return {
            "objects": objects,
            "object_count": len(objects),
            "spatial_distribution": self._get_spatial_distribution(objects)
        }
    
    def _classify_zone_object(self, zone: Any, zone_name: str, position: str) -> Dict:
        """Classify object in a zone"""
        if np is None or zone.size == 0:
            return {}
        
        mean_val = np.mean(zone)
        std_val = np.std(zone)
        variance = np.var(zone)
        
        # Classify based on properties
        obj_type = "unknown"
        confidence = 0.0
        
        if zone_name == "head":
            if std_val > 40:
                obj_type = "face_with_expression"
                confidence = 0.8
            elif std_val > 20:
                obj_type = "face"
                confidence = 0.7
            else:
                obj_type = "head_silhouette"
                confidence = 0.5
        
        elif zone_name == "torso":
            if std_val > 50:
                obj_type = "clothed_torso"
                confidence = 0.85
            elif std_val > 30:
                obj_type = "upper_body"
                confidence = 0.7
            else:
                obj_type = "torso_silhouette"
                confidence = 0.5
        
        elif "arm" in zone_name:
            if std_val > 30:
                obj_type = "arm_with_clothing"
                confidence = 0.8
            else:
                obj_type = "arm_silhouette"
                confidence = 0.6
        
        elif "leg" in zone_name:
            if std_val > 30:
                obj_type = "leg_with_clothing"
                confidence = 0.8
            else:
                obj_type = "leg_silhouette"
                confidence = 0.6
        
        return {
            "type": obj_type,
            "zone": zone_name,
            "position": position,
            "mean_brightness": float(mean_val),
            "std_deviation": float(std_val),
            "variance": float(variance),
            "confidence": confidence
        }
    
    def _get_spatial_distribution(self, objects: List[Dict]) -> Dict:
        """Get spatial distribution of objects"""
        distribution = {
            "foreground": [],
            "midground": [],
            "background": []
        }
        
        for obj in objects:
            if obj.get("confidence", 0) > 0.7:
                distribution["foreground"].append(obj)
            elif obj.get("confidence", 0) > 0.5:
                distribution["midground"].append(obj)
            else:
                distribution["background"].append(obj)
        
        return distribution
    
    # === Clothing Detection ===
    
    def _detect_clothing_items(self, img_array: Any, size: Tuple[int, int]) -> Dict:
        """Detect and classify clothing items"""
        if np is None:
            return {}
        
        height, width = img_array.shape[:2]
        gray = np.mean(img_array[:, :, :3], axis=2) if img_array.shape[2] >= 3 else img_array
        
        clothing_items = []
        
        # Upper body clothing
        upper_body = gray[int(height*0.25):int(height*0.6), int(width*0.2):int(width*0.8)]
        upper_clothing = self._classify_upper_clothing(upper_body)
        if upper_clothing:
            clothing_items.append(upper_clothing)
        
        # Lower body clothing
        lower_body = gray[int(height*0.6):int(height*0.95), int(width*0.25):int(width*0.75)]
        lower_clothing = self._classify_lower_clothing(lower_body)
        if lower_clothing:
            clothing_items.append(lower_clothing)
        
        # Footwear
        footwear = self._detect_footwear(img_array, height, width)
        if footwear:
            clothing_items.append(footwear)
        
        # Headwear
        headwear = self._detect_headwear(gray, height, width)
        if headwear:
            clothing_items.append(headwear)
        
        return {
            "items": clothing_items,
            "item_count": len(clothing_items),
            "style_analysis": self._analyze_clothing_style(clothing_items)
        }
    
    def _classify_upper_clothing(self, zone: Any) -> Dict:
        """Classify upper body clothing"""
        if np is None or zone.size == 0:
            return {}
        
        std_val = np.std(zone)
        mean_val = np.mean(zone)
        
        # Analyze texture and pattern
        dy, dx = np.gradient(zone)
        edge_density = float(np.sum(np.abs(dx) + np.abs(dy)) / zone.size)
        
        # Color analysis (if RGB)
        colors = []
        if zone.ndim == 3:
            colors = [
                {"r": int(np.mean(zone[:, :, 0])), "g": int(np.mean(zone[:, :, 1])), "b": int(np.mean(zone[:, :, 2]))}
            ]
        
        # Classify clothing type
        clothing_type = "unknown"
        if edge_density > 50:
            clothing_type = "textured_clothing"
        elif std_val > 40:
            clothing_type = "patterned_clothing"
        elif std_val > 20:
            clothing_type = "solid_clothing"
        else:
            clothing_type = "smooth_clothing"
        
        return {
            "type": clothing_type,
            "category": "upper_body",
            "mean_brightness": float(mean_val),
            "texture_complexity": float(edge_density),
            "colors": colors,
            "confidence": 0.8
        }
    
    def _classify_lower_clothing(self, zone: Any) -> Dict:
        """Classify lower body clothing"""
        if np is None or zone.size == 0:
            return {}
        
        std_val = np.std(zone)
        mean_val = np.mean(zone)
        
        dy, dx = np.gradient(zone)
        edge_density = float(np.sum(np.abs(dx) + np.abs(dy)) / zone.size)
        
        clothing_type = "unknown"
        if edge_density > 40:
            clothing_type = "textured_pants"
        elif std_val > 30:
            clothing_type = "patterned_pants"
        elif std_val > 15:
            clothing_type = "solid_pants"
        else:
            clothing_type = "smooth_pants"
        
        return {
            "type": clothing_type,
            "category": "lower_body",
            "mean_brightness": float(mean_val),
            "texture_complexity": float(edge_density),
            "confidence": 0.75
        }
    
    def _detect_footwear(self, img_array: Any, height: int, width: int) -> Dict:
        """Detect footwear"""
        if np is None:
            return {}
        
        gray = np.mean(img_array[:, :, :3], axis=2) if img_array.shape[2] >= 3 else img_array
        feet_zone = gray[int(height*0.9):, :]
        
        if feet_zone.size == 0:
            return {}
        
        std_val = np.std(feet_zone)
        mean_val = np.mean(feet_zone)
        
        return {
            "type": "footwear_detected",
            "category": "feet",
            "mean_brightness": float(mean_val),
            "std_deviation": float(std_val),
            "confidence": 0.6
        }
    
    def _detect_headwear(self, gray: Any, height: int, width: int) -> Dict:
        """Detect headwear"""
        if np is None:
            return {}
        
        head_zone = gray[int(height*0.05):int(height*0.25), int(width*0.3):int(width*0.7)]
        
        if head_zone.size == 0:
            return {}
        
        std_val = np.std(head_zone)
        mean_val = np.mean(head_zone)
        
        # Check for hat-like shape (higher edges)
        top_edge = head_zone[0, :]
        if np.std(top_edge) > 30:
            return {
                "type": "headwear_with_pattern",
                "category": "head",
                "mean_brightness": float(mean_val),
                "std_deviation": float(std_val),
                "confidence": 0.7
            }
        
        return {
            "type": "headwear_solid",
            "category": "head",
            "mean_brightness": float(mean_val),
            "std_deviation": float(std_val),
            "confidence": 0.5
        }
    
    def _analyze_clothing_style(self, items: List[Dict]) -> Dict:
        """Analyze overall clothing style"""
        if not items:
            return {}
        
        categories = [item.get("category", "") for item in items]
        types = [item.get("type", "") for item in items]
        
        # Determine style based on clothing types
        style = "casual"
        if any("formal" in t for t in types):
            style = "formal"
        elif any("textured" in t or "patterned" in t for t in types):
            style = "detailed"
        elif any("smooth" in t for t in types):
            style = "minimal"
        
        return {
            "overall_style": style,
            "categories": categories,
            "types": types
        }
    
    # === Accessories Detection ===
    
    def _detect_accessories(self, img_array: Any, size: Tuple[int, int]) -> Dict:
        """Detect accessories in image"""
        if np is None:
            return {}
        
        height, width = img_array.shape[:2]
        gray = np.mean(img_array[:, :, :3], axis=2) if img_array.shape[2] >= 3 else img_array
        
        accessories = []
        
        # Eyewear (eyes area)
        eyewear = self._detect_eyewear(gray, height, width)
        if eyewear:
            accessories.append(eyewear)
        
        # Jewelry (neck, wrists)
        jewelry = self._detect_jewelry(img_array, height, width)
        if jewelry:
            accessories.extend(jewelry)
        
        # Belts
        belt = self._detect_belt(gray, height, width)
        if belt:
            accessories.append(belt)
        
        return {
            "accessories": accessories,
            "accessory_count": len(accessories),
            "categories": list(set([acc.get("category", "unknown") for acc in accessories]))
        }
    
    def _detect_eyewear(self, gray: Any, height: int, width: int) -> Dict:
        """Detect eyewear (glasses, sunglasses)"""
        if np is None:
            return {}
        
        eye_zone = gray[int(height*0.2):int(height*0.35), int(width*0.35):int(width*0.65)]
        
        if eye_zone.size == 0:
            return {}
        
        # Look for high contrast horizontal lines (glasses frames)
        dy, dx = np.gradient(eye_zone)
        horizontal_edges = np.abs(dy)
        
        if np.mean(horizontal_edges) > 20:
            return {
                "type": "eyewear",
                "category": "face",
                "confidence": 0.7
            }
        
        return {}
    
    def _detect_jewelry(self, img_array: Any, height: int, width: int) -> List[Dict]:
        """Detect jewelry (necklace, bracelet, ring)"""
        if np is None:
            return []
        
        gray = np.mean(img_array[:, :, :3], axis=2) if img_array.shape[2] >= 3 else img_array
        accessories = []
        
        # Necklace (neck area)
        neck_zone = gray[int(height*0.3):int(height*0.4), int(width*0.4):int(width*0.6)]
        if neck_zone.size > 0 and np.std(neck_zone) > 25:
            accessories.append({
                "type": "necklace",
                "category": "neck",
                "confidence": 0.6
            })
        
        # Bracelets (wrist areas)
        wrist_left = gray[int(height*0.6):int(height*0.7), int(width*0.1):int(width*0.2)]
        wrist_right = gray[int(height*0.6):int(height*0.7), int(width*0.8):int(width*0.9)]
        
        if np.std(wrist_left) > 20:
            accessories.append({
                "type": "bracelet",
                "category": "wrist",
                "side": "left",
                "confidence": 0.5
            })
        
        if np.std(wrist_right) > 20:
            accessories.append({
                "type": "bracelet",
                "category": "wrist",
                "side": "right",
                "confidence": 0.5
            })
        
        return accessories
    
    def _detect_belt(self, gray: Any, height: int, width: int) -> Dict:
        """Detect belt"""
        if np is None:
            return {}
        
        waist_zone = gray[int(height*0.55):int(height*0.65), int(width*0.25):int(width*0.75)]
        
        if waist_zone.size == 0:
            return {}
        
        # Look for horizontal line (belt)
        dy, dx = np.gradient(waist_zone)
        horizontal_contrast = np.mean(np.abs(dy))
        
        if horizontal_contrast > 30:
            return {
                "type": "belt",
                "category": "waist",
                "horizontal_contrast": float(horizontal_contrast),
                "confidence": 0.7
            }
        
        return {}
    
    # === 3D Structure Analysis ===
    
    def _analyze_3d_structure(self, img_array: Any, size: Tuple[int, int]) -> Dict:
        """Analyze 3D structure and occlusion"""
        if np is None:
            return {}
        
        height, width = img_array.shape[:2]
        gray = np.mean(img_array[:, :, :3], axis=2) if img_array.shape[2] >= 3 else img_array
        
        # Compute surface normals from shading
        normals = self._compute_surface_normals(gray)
        
        # Detect occlusion boundaries
        occlusions = self._detect_occlusions(gray)
        
        # Estimate depth from shading
        depth_map = self._estimate_depth_from_shading(gray, normals)
        
        # Analyze object volumes
        volumes = self._estimate_volumes(gray, height, width)
        
        # Back-side inference
        back_inference = self._infer_back_structure(gray, volumes)
        
        return {
            "surface_normals": {
                "mean_x": float(np.mean(normals[:, 0])) if len(normals) > 0 else 0,
                "mean_y": float(np.mean(normals[:, 1])) if len(normals) > 0 else 0,
                "mean_z": float(np.mean(normals[:, 2])) if len(normals) > 0 else 0
            },
            "occlusions": occlusions,
            "depth_map_stats": {
                "mean_depth": float(np.mean(depth_map)) if depth_map.size > 0 else 0,
                "depth_variance": float(np.var(depth_map)) if depth_map.size > 0 else 0,
                "depth_range": [float(np.min(depth_map)), float(np.max(depth_map))] if depth_map.size > 0 else [0, 0]
            },
            "volumes": volumes,
            "back_structure_inference": back_inference,
            "3d_confidence": self._calculate_3d_confidence(normals, occlusions, volumes)
        }
    
    def _compute_surface_normals(self, gray: Any) -> Any:
        """Compute approximate surface normals from shading"""
        if np is None:
            return np.array([])
        
        dy, dx = np.gradient(gray)
        
        # Approximate normals
        normals = np.zeros((gray.shape[0], gray.shape[1], 3), dtype=np.float32)
        normals[:, :, 0] = -dx  # x component
        normals[:, :, 1] = -dy  # y component
        normals[:, :, 2] = 1    # z component (assuming front-facing)
        
        # Normalize
        magnitude = np.sqrt(np.sum(normals**2, axis=2, keepdims=True))
        magnitude = np.where(magnitude == 0, 1, magnitude)
        normals = normals / magnitude
        
        return normals
    
    def _detect_occlusions(self, gray: Any) -> List[Dict]:
        """Detect occlusion boundaries"""
        if np is None:
            return []
        
        dy, dx = np.gradient(gray)
        edge_magnitude = np.sqrt(dx**2 + dy**2)
        
        # Find strong edges (potential occlusions)
        threshold = np.percentile(edge_magnitude, 90)
        occlusion_mask = edge_magnitude > threshold
        
        occlusions = []
        if np.any(occlusion_mask):
            # Find connected components (simplified)
            occlusions.append({
                "type": "occlusion_boundary",
                "location": "multiple",
                "strength": float(np.mean(edge_magnitude[occlusion_mask])),
                "extent": float(np.sum(occlusion_mask) / occlusion_mask.size)
            })
        
        return occlusions
    
    def _estimate_depth_from_shading(self, gray: Any, normals: Any) -> Any:
        """Estimate depth map from shading and normals"""
        if np is None or gray.size == 0:
            return []
        
        # Simplified depth estimation from shading
        # Brighter areas assumed closer (simplified model)
        depth_map = 1.0 - (gray - np.min(gray)) / (np.max(gray) - np.min(gray) + 1e-6)
        
        return depth_map
    
    def _estimate_volumes(self, gray: Any, height: int, width: int) -> List[Dict]:
        """Estimate volumes of detected objects"""
        if np is None:
            return []
        
        volumes = []
        
        # Head volume
        head_zone = gray[int(height*0.05):int(height*0.35), int(width*0.3):int(width*0.7)]
        if head_zone.size > 0:
            volumes.append({
                "object": "head",
                "estimated_volume": float(head_zone.size * np.mean(head_zone) / 255.0),
                "shape": "ellipsoid",
                "confidence": 0.7
            })
        
        # Torso volume
        torso_zone = gray[int(height*0.35):int(height*0.65), int(width*0.2):int(width*0.8)]
        if torso_zone.size > 0:
            volumes.append({
                "object": "torso",
                "estimated_volume": float(torso_zone.size * np.mean(torso_zone) / 255.0),
                "shape": "cylinder",
                "confidence": 0.75
            })
        
        # Arm volumes
        arm_left = gray[int(height*0.35):int(height*0.65), int(width*0.05):int(width*0.2)]
        arm_right = gray[int(height*0.35):int(height*0.65), int(width*0.8):int(width*0.95)]
        
        for i, arm_zone in enumerate([arm_left, arm_right]):
            if arm_zone.size > 0:
                volumes.append({
                    "object": f"arm_{i+1}",
                    "estimated_volume": float(arm_zone.size * np.mean(arm_zone) / 255.0),
                    "shape": "cylinder",
                    "confidence": 0.6
                })
        
        # Leg volumes
        leg_left = gray[int(height*0.65):int(height*0.95), int(width*0.3):int(width*0.45)]
        leg_right = gray[int(height*0.65):int(height*0.95), int(width*0.55):int(width*0.7)]
        
        for i, leg_zone in enumerate([leg_left, leg_right]):
            if leg_zone.size > 0:
                volumes.append({
                    "object": f"leg_{i+1}",
                    "estimated_volume": float(leg_zone.size * np.mean(leg_zone) / 255.0),
                    "shape": "cylinder",
                    "confidence": 0.65
                })
        
        return volumes
    
    def _infer_back_structure(self, gray: Any, volumes: List[Dict]) -> Dict:
        """Infer back-side structure from front-side analysis"""
        if np is None:
            return {}
        
        inferences = []
        
        for volume in volumes:
            obj = volume.get("object", "")
            shape = volume.get("shape", "")
            
            if obj == "head":
                inferences.append({
                    "object": "head",
                    "front_analysis": volume,
                    "back_inference": {
                        "shape": "curved",
                        "features": ["occipital_bulge", "hair_coverage"],
                        "symmetry": "high"
                    }
                })
            
            elif obj == "torso":
                inferences.append({
                    "object": "torso",
                    "front_analysis": volume,
                    "back_inference": {
                        "shape": "curved_flat",
                        "features": ["spine", "scapulae", "muscle_layers"],
                        "symmetry": "medium"
                    }
                })
            
            elif "arm" in obj:
                inferences.append({
                    "object": obj,
                    "front_analysis": volume,
                    "back_inference": {
                        "shape": "cylindrical",
                        "features": ["muscle_groups", "joint_bulges"],
                        "symmetry": "high"
                    }
                })
            
            elif "leg" in obj:
                inferences.append({
                    "object": obj,
                    "front_analysis": volume,
                    "back_inference": {
                        "shape": "cylindrical",
                        "features": ["muscle_groups", "joint_bulges", "gluteal_region"],
                        "symmetry": "high"
                    }
                })
        
        return {
            "inferences": inferences,
            "overall_symmetry": "high",
            "confidence": 0.7
        }
    
    def _calculate_3d_confidence(self, normals: Any, occlusions: List[Dict], volumes: List[Dict]) -> float:
        """Calculate confidence in 3D analysis"""
        if np is None or len(volumes) == 0:
            return 0.0
        
        # Base confidence from volume detection
        base_confidence = min(1.0, len(volumes) * 0.2)
        
        # Occlusion increases confidence (more depth cues)
        occlusion_factor = min(1.0, len(occlusions) * 0.3)
        
        # Normal consistency
        normal_consistency = 0.5
        if len(normals) > 0:
            normal_std = np.std(normals)
            normal_consistency = max(0.0, 1.0 - normal_std)
        
        return float(min(1.0, base_confidence + occlusion_factor * 0.3 + normal_consistency * 0.2))
    
    # === Helper methods ===
    
    def _estimate_curvature(self, zone: Any) -> str:
        if np is None or zone.size == 0:
            return "flat"
        std = np.std(zone)
        if std > 50:
            return "high_curvature"
        elif std > 25:
            return "medium_curvature"
        return "low_curvature"
    
    def _estimate_fabric_tension(self, zone: Any) -> str:
        if np is None or zone.size == 0:
            return "loose"
        contrast = np.std(zone) / (np.mean(zone) + 1e-6)
        if contrast > 0.3:
            return "tight"
        elif contrast > 0.15:
            return "medium"
        return "loose"
    
    def _estimate_muscle_definition(self, zone: Any) -> str:
        if np is None or zone.size == 0:
            return "none"
        std = np.std(zone)
        if std > 40:
            return "high"
        elif std > 20:
            return "medium"
        return "low"
    
    def _classify_drapery(self, tension_zones: Dict) -> str:
        if np is None:
            return "loose"
        avg_tension = np.mean(list(tension_zones.values()))
        if avg_tension > 50:
            return "tight_fitting"
        elif avg_tension > 25:
            return "fitted"
        return "loose"
    
    def _classify_fit(self, tension_zones: Dict) -> str:
        chest = tension_zones.get("chest", 0)
        waist = tension_zones.get("waist", 0)
        
        if chest > 40 and waist < 20:
            return "athletic"
        elif chest > 30:
            return "fitted"
        return "loose"
    
    def _determine_light_direction(self, left: Any, right: Any) -> str:
        if np is None:
            return "front"
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
        if np is None:
            return "soft"
        gray = np.mean(img_array[:, :, :3], axis=2)
        dy, dx = np.gradient(gray)
        edge_width = float(np.mean(np.sqrt(dx**2 + dy**2)))
        
        if edge_width > 40:
            return "hard"
        elif edge_width > 20:
            return "soft"
        return "very_soft"
    
    def _classify_lighting(self, contrast: float, shadow_softness: str) -> str:
        if contrast > 0.5:
            return "dramatic"
        elif contrast > 0.3:
            return "balanced"
        return "flat"
    
    def _find_highlights(self, img_array: Any) -> List[str]:
        if np is None:
            return ["center"]
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
        if np is None:
            return "matte"
        if np.sum(bright_areas) / bright_areas.size < 0.01:
            return "matte"
        
        bright_coords = np.argwhere(bright_areas)
        if len(bright_coords) == 0:
            return "matte"
        
        if np.std(bright_coords[:, 0]) < 10 and np.std(bright_coords[:, 1]) < 10:
            return "specular_point"
        
        return "diffuse_gloss"
    
    def _analyze_reflections(self, img_array: Any, bright_areas: Any) -> Dict:
        if np is None:
            return {"intensity": 0, "clarity": "soft"}
        return {
            "intensity": float(np.sum(bright_areas) / bright_areas.size),
            "clarity": "sharp" if np.sum(bright_areas) < bright_areas.size * 0.05 else "soft"
        }
    
    def _detect_wet_surfaces(self, img_array: Any) -> bool:
        if np is None:
            return False
        rgb_mean = np.mean(img_array[:, :, :3], axis=2)
        bright_areas = rgb_mean > 220
        
        if np.sum(bright_areas) / bright_areas.size > 0.05:
            return True
        return False
    
    def _detect_eye_glint(self, img_array: Any) -> bool:
        if np is None:
            return False
        height, width = img_array.shape[:2]
        
        eye_zone = img_array[int(height*0.2):int(height*0.35), int(width*0.35):int(width*0.65)]
        
        if eye_zone.size == 0:
            return False
        
        rgb_mean = np.mean(eye_zone[:, :, :3], axis=2)
        bright = rgb_mean > 200
        
        return np.sum(bright) > 5 and np.sum(bright) < eye_zone.size * 0.1
    
    def _classify_composition(self, sharpness: Dict, contrast: Dict) -> str:
        fg = sharpness.get("foreground", 0)
        bg = sharpness.get("background", 0)
        
        if fg > bg * 1.5:
            return "shallow_depth"
        elif abs(fg - bg) < 10:
            return "deep_focus"
        return "selective_focus"
    
    def _classify_emotion(self, face_gray: Any, shadows: Any, highlights: Any) -> str:
        if np is None:
            return "unknown"
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
        if np is None or face_gray.size == 0:
            return "relaxed"
        gradient = np.abs(np.gradient(face_gray))
        if np.mean(gradient) > 30:
            return "tense"
        return "relaxed"
    
    def _estimate_body_contours(self, zone: Any) -> bool:
        if np is None or zone.size == 0:
            return False
        return bool(np.std(zone) > 30)
    
    def _classify_body_type(self, muscle_def: Dict) -> str:
        chest = muscle_def.get("chest", 0)
        arms = muscle_def.get("arms", 0)
        
        if chest > 40 and arms > 40:
            return "athletic"
        elif chest > 30:
            return "muscular"
        return "slim"
    
    def _estimate_muscle_visibility(self, gradient_magnitude: Any) -> bool:
        if np is None:
            return False
        return float(np.mean(gradient_magnitude)) > 25
    
    def _calculate_depth_score(self, sharpness: Dict) -> float:
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
                "muscle_structure": len(self.knowledge["muscle_structure"]),
                "objects": len(self.knowledge["objects"]),
                "clothing_items": len(self.knowledge["clothing_items"]),
                "accessories": len(self.knowledge["accessories"]),
                "3d_structure": len(self.knowledge["3d_structure"])
            }
        }


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
