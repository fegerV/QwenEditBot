#!/usr/bin/env python3
"""Populate database with initial data"""

import sqlite3

def populate_database():
    """Add initial data to the database"""
    print("Populating database with initial data...")
    
    with sqlite3.connect('backend/qwen.db') as conn:
        cursor = conn.cursor()
        
        # Clear existing presets if any
        cursor.execute('DELETE FROM presets;')
        
        # Insert default presets with workflow_type
        presets_data = [
            ('styles', 'Oil Painting', '🖌', 'Convert the image into an oil painting style with visible brush strokes, rich colors, and a classical artistic feel, while preserving the original composition.', 30.0, 1, 'qwen_edit_2511'),
            ('styles', 'Watercolor', '💧', 'Convert the image into a watercolor painting with soft edges, light color bleeding, and a hand-painted artistic look, preserving the main details.', 30.0, 2, 'qwen_edit_2511'),
            ('styles', 'Pencil Sketch', '✏️', 'Transform the image into a detailed pencil sketch with clear linework and shading, like a hand-drawn illustration.', 30.0, 3, 'qwen_edit_2511'),
            ('styles', 'Ink Drawing', '🖋', 'Convert the image into an ink drawing with bold black outlines, high contrast, and a clean hand-drawn style.', 30.0, 4, 'qwen_edit_2511'),
            
            ('portrait', 'Studio Portrait', '📸', 'Enhance the image into a professional studio portrait with soft lighting, realistic skin texture, and natural colors, preserving facial identity.', 30.0, 1, 'qwen_edit_2511'),
            ('portrait', 'Cinematic Portrait', '🎬', 'Convert the portrait into a cinematic style with dramatic lighting, shallow depth of field, and a movie-like atmosphere, while keeping the person\'s identity.', 30.0, 2, 'qwen_edit_2511'),
            ('portrait', 'Artistic Portrait', '🧑‍🎨', 'Create an artistic portrait with expressive lighting and painterly details, preserving facial features and overall composition.', 30.0, 3, 'qwen_edit_2511'),
            
            ('product', 'E-commerce', '🛒', 'Transform the image into a clean professional product photo with neutral background, even lighting, and sharp details suitable for an online store.', 30.0, 1, 'qwen_edit_2511'),
            ('product', 'Premium Product', '🌟', 'Enhance the product image with dramatic lighting, glossy reflections, and a premium advertising look, keeping the product shape unchanged.', 30.0, 2, 'qwen_edit_2511'),
            
            ('lighting', 'Soft Light', '🌞', 'Adjust the image to have soft, natural lighting with smooth shadows and a warm, pleasant atmosphere.', 30.0, 1, 'qwen_edit_2511'),
            ('lighting', 'Dark Mood', '🌙', 'Create a dark and moody atmosphere with low-key lighting, deep shadows, and cinematic contrast.', 30.0, 2, 'qwen_edit_2511'),
            ('lighting', 'Golden Hour', '🌅', 'Apply golden hour lighting with warm tones, soft highlights, and a sunset-like atmosphere.', 30.0, 3, 'qwen_edit_2511'),
            
            ('animation', 'Comic Book', '💥', 'Convert the image into a comic book style with bold outlines, flat colors, and a graphic illustrated look.', 30.0, 1, 'qwen_edit_2511'),
            ('animation', 'Anime', '🇯🇵', 'Transform the image into an anime style illustration with clean lines, expressive features, and vibrant colors.', 30.0, 2, 'qwen_edit_2511'),
            ('animation', 'Cartoon', '🧸', 'Convert the image into a cartoon style with simplified shapes, bright colors, and a playful illustrated look.', 30.0, 3, 'qwen_edit_2511'),
            
            ('enhancement', 'Improve Quality', '✨', 'Improve image quality by enhancing details, colors, and lighting while keeping the original style and composition unchanged.', 30.0, 1, 'qwen_edit_2511'),
        ]
        
        for preset in presets_data:
            cursor.execute('''
                INSERT INTO presets (category, name, icon, prompt, price, "order", workflow_type) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', preset)
        
        conn.commit()
        
        # Verify the insertion
        cursor.execute('SELECT COUNT(*) FROM presets;')
        count = cursor.fetchone()[0]
        print(f"Successfully added {count} presets to the database")
        
        # Show sample of inserted data
        cursor.execute('SELECT name, category, price FROM presets LIMIT 5;')
        records = cursor.fetchall()
        print('Sample of inserted presets:')
        for record in records:
            print(f'  {record[0]} ({record[1]}) - {record[2]} points')

if __name__ == "__main__":
    populate_database()