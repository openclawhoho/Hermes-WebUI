"""
獨立的漫畫刪除路由模塊
從 manga_daily_update.json 和 manga_komga_mapping.json 中刪除指定漫畫
"""
import json
import os
from api.routes import j, MANGA_DAILY_UPDATE_FILE, MANGA_KOMGA_MAPPING_FILE, logger

def handle_delete(handler, parsed):
    """處理 /api/manga/delete 請求"""
    try:
        content_length = int(handler.headers.get('Content-Length', 0))
        body = json.loads(handler.rfile.read(content_length).decode('utf-8'))
        manga_name = body.get('name', '').strip()
        
        if not manga_name:
            return j(handler, {'success': False, 'error': '缺少漫畫名稱'}, status=400)
        
        # 從 manga_daily_update.json 刪除
        if not os.path.exists(MANGA_DAILY_UPDATE_FILE):
            return j(handler, {'success': False, 'error': '資料文件不存在'}, status=404)
        
        with open(MANGA_DAILY_UPDATE_FILE, 'r', encoding='utf-8') as f:
            updates_data = json.load(f)
        
        original_count = len(updates_data)
        updates_data = [item for item in updates_data if item.get('name') != manga_name]
        deleted_count = original_count - len(updates_data)
        
        if deleted_count == 0:
            return j(handler, {'success': False, 'error': f'找不到漫畫: {manga_name}'}, status=404)
        
        with open(MANGA_DAILY_UPDATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(updates_data, f, ensure_ascii=False, indent=2)
        
        # 從映射文件也刪除
        try:
            if os.path.exists(MANGA_KOMGA_MAPPING_FILE):
                with open(MANGA_KOMGA_MAPPING_FILE, 'r', encoding='utf-8') as f:
                    mapping = json.load(f)
                
                mapping = [item for item in mapping if item.get('name_trad') != manga_name]
                
                with open(MANGA_KOMGA_MAPPING_FILE, 'w', encoding='utf-8') as f:
                    json.dump(mapping, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.debug(f"刪除映射文件條目失敗: {e}")
        
        return j(handler, {
            'success': True,
            'message': f'已刪除漫畫: {manga_name}',
            'deleted_count': deleted_count
        })
    except Exception as e:
        return j(handler, {'error': str(e)}, status=500)
