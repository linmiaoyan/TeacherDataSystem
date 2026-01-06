"""
PDF处理服务
用于在PDF指定位置添加文本
"""
from pathlib import Path
from typing import Dict, Any, List, Tuple
import shutil

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from PyPDF2 import PdfReader, PdfWriter
    from reportlab.lib.units import mm
    PDF_LIBRARIES_AVAILABLE = True
except ImportError:
    PDF_LIBRARIES_AVAILABLE = False
    print("警告: PDF处理库未安装，请安装: pip install reportlab PyPDF2")


def get_pdf_page_size(pdf_path: str, page_num: int = 0) -> Tuple[float, float]:
    """
    获取PDF页面尺寸（以点为单位，1点=1/72英寸）
    返回 (width, height)
    """
    if not PDF_LIBRARIES_AVAILABLE:
        return (595, 842)  # A4默认尺寸
    
    try:
        reader = PdfReader(pdf_path)
        if page_num < len(reader.pages):
            page = reader.pages[page_num]
            # 获取页面尺寸（以点为单位）
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)
            return (width, height)
    except Exception as e:
        print(f"获取PDF页面尺寸失败: {e}")
    
    return (595, 842)  # A4默认尺寸


def add_text_to_pdf(
    template_path: str,
    output_path: str,
    text_positions: List[Dict[str, Any]],
    data: Dict[str, Any]
):
    """
    在PDF的指定位置添加文本
    
    Args:
        template_path: 模板PDF路径
        output_path: 输出PDF路径
        text_positions: 文本位置列表，格式：
            [{
                "field_name": "name",
                "page": 0,  # 页码（从0开始）
                "x": 100,   # X坐标（以点为单位，左下角为原点）
                "y": 700,   # Y坐标（以点为单位，左下角为原点）
                "font_size": 12,  # 字体大小（可选，默认12）
                "font_name": "Helvetica"  # 字体名称（可选）
            }]
        data: 教师数据字典
    """
    if not PDF_LIBRARIES_AVAILABLE:
        raise ImportError("PDF处理库未安装，请安装: pip install reportlab PyPDF2")
    
    # 复制模板文件
    shutil.copy(template_path, output_path)
    
    try:
        # 读取PDF
        reader = PdfReader(output_path)
        writer = PdfWriter()
        
        # 按页码分组文本位置
        positions_by_page = {}
        for pos in text_positions:
            page_num = pos.get("page", 0)
            if page_num not in positions_by_page:
                positions_by_page[page_num] = []
            positions_by_page[page_num].append(pos)
        
        # 处理每一页
        print(f"[PDF处理] 开始处理PDF，总页数: {len(reader.pages)}, 需要处理的占位符: {len(text_positions)}")
        for page_num in range(len(reader.pages)):
            print(f"[PDF处理] 处理第 {page_num + 1}/{len(reader.pages)} 页...")
            page = reader.pages[page_num]
            
            # 获取页面尺寸
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            print(f"[PDF处理] 页面尺寸: {page_width} x {page_height}")
            
            # 如果这一页有文本要添加
            if page_num in positions_by_page:
                print(f"[PDF处理] 第 {page_num + 1} 页有 {len(positions_by_page[page_num])} 个占位符需要处理")
                # 创建临时PDF用于添加文本或图片
                from io import BytesIO
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter
                try:
                    from PIL import Image as PILImage
                    PIL_AVAILABLE = True
                except ImportError:
                    PIL_AVAILABLE = False
                
                packet = BytesIO()
                can = canvas.Canvas(packet, pagesize=(page_width, page_height))
                
                # 设置中文字体支持
                font_name = "SimSun"  # 默认使用SimSun（宋体）
                try:
                    from reportlab.pdfbase.ttfonts import TTFont
                    from reportlab.pdfbase import pdfmetrics
                    import os
                    import platform
                    
                    # 尝试查找系统中文字体
                    system_fonts = []
                    if platform.system() == "Windows":
                        # Windows系统字体路径
                        font_dirs = [
                            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts"),
                            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts"),
                        ]
                        for font_dir in font_dirs:
                            if os.path.exists(font_dir):
                                # 查找常见中文字体
                                for font_file in ["simsun.ttc", "simsun.ttf", "simhei.ttf", "msyh.ttf", "msyhbd.ttf"]:
                                    font_path = os.path.join(font_dir, font_file)
                                    if os.path.exists(font_path):
                                        system_fonts.append((font_path, font_file.split(".")[0].title()))
                                        break
                    elif platform.system() == "Linux":
                        # Linux系统字体路径
                        font_dirs = ["/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts")]
                        for font_dir in font_dirs:
                            if os.path.exists(font_dir):
                                for root, dirs, files in os.walk(font_dir):
                                    for file in files:
                                        if file.lower().endswith((".ttf", ".ttc", ".otf")):
                                            if any(keyword in file.lower() for keyword in ["song", "simsun", "simhei", "noto"]):
                                                system_fonts.append((os.path.join(root, file), "ChineseFont"))
                                                break
                    elif platform.system() == "Darwin":  # macOS
                        font_dirs = ["/System/Library/Fonts", "/Library/Fonts", os.path.expanduser("~/Library/Fonts")]
                        for font_dir in font_dirs:
                            if os.path.exists(font_dir):
                                for file in os.listdir(font_dir):
                                    if file.lower().endswith((".ttf", ".ttc", ".otf")):
                                        if any(keyword in file.lower() for keyword in ["song", "simsun", "simhei", "pingfang"]):
                                            system_fonts.append((os.path.join(font_dir, file), "ChineseFont"))
                                            break
                    
                    # 注册找到的第一个中文字体
                    if system_fonts:
                        font_path, font_display_name = system_fonts[0]
                        try:
                            pdfmetrics.registerFont(TTFont('SimSun', font_path))
                            font_name = "SimSun"
                            print(f"已注册中文字体: {font_display_name} ({font_path})")
                        except Exception as e:
                            print(f"注册中文字体失败: {e}")
                            # 如果注册失败，尝试使用reportlab内置的中文字体
                            try:
                                from reportlab.pdfbase.cidfonts import UnicodeCIDFont
                                pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
                                font_name = "STSong-Light"
                                print("使用reportlab内置中文字体: STSong-Light")
                            except:
                                pass
                    else:
                        # 如果没有找到系统字体，尝试使用reportlab内置的中文字体
                        try:
                            from reportlab.pdfbase.cidfonts import UnicodeCIDFont
                            pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
                            font_name = "STSong-Light"
                            print("使用reportlab内置中文字体: STSong-Light")
                        except Exception as e:
                            print(f"无法加载中文字体: {e}")
                            # 最后使用Helvetica，但中文会显示为方块
                            font_name = "Helvetica"
                            print("警告: 未找到中文字体，中文可能显示异常")
                except Exception as e:
                    print(f"字体设置出错: {e}")
                    font_name = "Helvetica"
                
                # 在指定位置添加文本
                for pos_index, pos in enumerate(positions_by_page[page_num], 1):
                    field_name = pos.get("field_name", "")
                    x = pos.get("x", 0)
                    y = pos.get("y", 0)
                    font_size = pos.get("font_size", 12)
                    pos_font_name = pos.get("font_name", font_name)  # 使用位置指定的字体或默认中文字体
                    
                    print(f"[PDF处理] 处理占位符 {pos_index}/{len(positions_by_page[page_num])}: {field_name}, 位置: ({x}, {y})")
                    
                    # 检查是否为常量
                    if pos.get("is_constant") and pos.get("constant_value"):
                        # 直接使用常量值
                        value = pos.get("constant_value", "")
                        print(f"[PDF处理] 常量字段: {field_name} = {value}")
                    else:
                        # 获取字段值
                        value = data.get(field_name, "")
                        if not value and "extra_data" in data and isinstance(data["extra_data"], dict):
                            value = data["extra_data"].get(field_name, "")
                        value_str = str(value) if value else ""
                        print(f"[PDF处理] 字段: {field_name}, 值类型: {type(value)}, 值长度: {len(value_str)}")
                    
                    if value is None:
                        value = ""
                    
                    # 检查是否是图片数据（base64格式）
                    is_image = False
                    image_data = None
                    if isinstance(value, str) and value.startswith("data:image"):
                        is_image = True
                        # 解析base64图片数据
                        import base64
                        try:
                            print(f"[PDF处理] 检测到图片字段: {field_name}, 数据长度: {len(value)}")
                            # 格式: data:image/png;base64,xxxxx
                            header, encoded = value.split(',', 1)
                            print(f"[PDF处理] 开始解码base64图片数据...")
                            image_data = base64.b64decode(encoded)
                            print(f"[PDF处理] base64解码成功, 图片数据大小: {len(image_data)} bytes")
                        except Exception as e:
                            print(f"[PDF处理] 解析base64图片失败 (字段: {field_name}): {e}")
                            import traceback
                            traceback.print_exc()
                            is_image = False
                    
                    if is_image and image_data and PIL_AVAILABLE:
                        # 添加图片到PDF
                        try:
                            print(f"[PDF处理] 开始处理图片 (字段: {field_name})...")
                            from io import BytesIO
                            print(f"[PDF处理] 使用PIL打开图片...")
                            img = PILImage.open(BytesIO(image_data))
                            print(f"[PDF处理] 图片打开成功, 原始尺寸: {img.size}")
                            
                            # 根据字体大小计算合适的图片尺寸
                            # 中文字符宽度大约是字体大小的1倍（等宽字体）
                            # 假设签名区域应该和2-3个中文字符的宽度差不多
                            # 使用字体大小的2.5倍作为目标宽度，高度按比例缩放
                            target_width = font_size * 2.5  # 约2-3个字的宽度
                            target_height = font_size * 1.0  # 高度约为字体大小，保持签名的手写感
                            
                            print(f"[PDF处理] 字体大小: {font_size}, 目标尺寸: {target_width} x {target_height} 点")
                            
                            img_width, img_height = img.size
                            print(f"[PDF处理] 图片原始尺寸: {img_width} x {img_height} 像素")
                            
                            # 计算缩放比例，保持宽高比，以宽度为主
                            width_ratio = target_width / img_width
                            height_ratio = target_height / img_height
                            # 使用较小的比例，确保图片不会超出目标区域
                            ratio = min(width_ratio, height_ratio)
                            
                            # 如果图片比目标尺寸小，不放大（保持原始清晰度）
                            if ratio > 1.0:
                                ratio = 1.0
                                print(f"[PDF处理] 图片小于目标尺寸，保持原始大小")
                            else:
                                print(f"[PDF处理] 图片缩放比例: {ratio:.2f}")
                            
                            img_width = int(img_width * ratio)
                            img_height = int(img_height * ratio)
                            
                            # 确保不超过目标尺寸
                            if img_width > target_width:
                                img_width = int(target_width)
                            if img_height > target_height:
                                img_height = int(target_height)
                            
                            print(f"[PDF处理] 缩放后尺寸: {img_width} x {img_height} 点")
                            
                            if ratio < 1.0:
                                img = img.resize((img_width, img_height), PILImage.Resampling.LANCZOS)
                                print(f"[PDF处理] 图片缩放完成")
                            
                            # 将PIL图片转换为reportlab可用的格式
                            print(f"[PDF处理] 转换图片格式为PNG...")
                            img_buffer = BytesIO()
                            # 优化：如果图片已经是PNG格式且尺寸合适，直接使用
                            if img.format == 'PNG' and img_width <= target_width and img_height <= target_height:
                                # 直接保存，不重新编码
                                img.save(img_buffer, format='PNG', optimize=True)
                            else:
                                # 转换为PNG并优化
                                img.save(img_buffer, format='PNG', optimize=True, compress_level=6)
                            img_buffer.seek(0)
                            buffer_size = len(img_buffer.getvalue())
                            print(f"[PDF处理] 图片格式转换完成, 缓冲区大小: {buffer_size} bytes")
                            
                            # 使用reportlab添加图片
                            # 注意：保存的坐标y已经是PDF坐标系（左下角为原点，Y向上）
                            # reportlab的Canvas也是左下角为原点，所以直接使用y
                            from reportlab.lib.utils import ImageReader
                            print(f"[PDF处理] 添加图片到PDF, 位置: ({x}, {y - img_height}), 尺寸: ({img_width}, {img_height})")
                            can.drawImage(ImageReader(img_buffer), x, y - img_height, 
                                        width=img_width, height=img_height)
                            print(f"[PDF处理] 图片添加成功 (字段: {field_name})")
                            
                            # 清理内存
                            img.close()
                            img_buffer.close()
                        except Exception as e:
                            print(f"[PDF处理] 添加图片失败 (字段: {field_name}): {e}")
                            import traceback
                            traceback.print_exc()
                            # 如果图片处理失败，跳过这个字段，继续处理其他字段
                    else:
                        # 添加文本（使用UTF-8编码确保中文正确显示）
                        value = str(value)
                        try:
                            can.setFont(pos_font_name, font_size)
                            # 确保文本是UTF-8编码
                            if isinstance(value, bytes):
                                value = value.decode('utf-8')
                            # 注意：保存的坐标y已经是PDF坐标系（左下角为原点，Y向上）
                            # reportlab的Canvas也是左下角为原点，所以直接使用y
                            can.drawString(x, y, value)
                        except Exception as e:
                            print(f"添加文本失败 (字段: {field_name}, 值: {value[:20]}): {e}")
                            # 如果字体不支持，尝试使用默认字体
                            try:
                                can.setFont("Helvetica", font_size)
                                can.drawString(x, y, value)
                            except:
                                pass
                
                print(f"[PDF处理] 保存canvas...")
                can.save()
                
                # 将新页面合并到原页面
                print(f"[PDF处理] 合并页面...")
                packet.seek(0)
                new_pdf = PdfReader(packet)
                new_page = new_pdf.pages[0]
                
                # 合并页面
                page.merge_page(new_page)
                print(f"[PDF处理] 第 {page_num + 1} 页处理完成")
            
            writer.add_page(page)
        
        # 保存结果
        print(f"[PDF处理] 保存最终PDF文件: {output_path}")
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        print(f"[PDF处理] PDF处理完成: {output_path}")
    
    except Exception as e:
        print(f"[PDF处理] PDF处理失败: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"处理PDF失败: {str(e)}")


def extract_placeholders_from_pdf(pdf_path: str) -> List[str]:
    """
    从PDF中提取占位符（目前PDF不支持自动提取，返回空列表）
    占位符位置信息存储在数据库的placeholder_positions字段中
    """
    # PDF文件无法像Word/Excel那样自动提取占位符
    # 占位符位置由用户在界面上拖动选择后保存
    return []


def get_pdf_preview(pdf_path: str, page_num: int = 0) -> bytes:
    """
    获取PDF页面的预览图片（用于前端显示）
    返回PNG格式的图片字节
    """
    if not PDF_LIBRARIES_AVAILABLE:
        raise ImportError("PDF处理库未安装")
    
    try:
        from pdf2image import convert_from_path
        images = convert_from_path(pdf_path, first_page=page_num + 1, last_page=page_num + 1)
        if images:
            from io import BytesIO
            img_byte_arr = BytesIO()
            images[0].save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
        else:
            raise Exception("无法生成预览图片")
    except ImportError:
        # 如果没有pdf2image，返回一个占位图片
        from io import BytesIO
        from PIL import Image, ImageDraw, ImageFont
        # 创建一个简单的占位图片
        img = Image.new('RGB', (595, 842), color='white')
        draw = ImageDraw.Draw(img)
        text = f"PDF预览功能需要安装pdf2image库\npip install pdf2image\n还需要安装poppler"
        try:
            # 尝试使用默认字体
            font = ImageFont.load_default()
        except:
            font = None
        draw.text((50, 400), text, fill='black', font=font)
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    except Exception as e:
        # 如果生成预览失败，返回一个错误提示图片
        from io import BytesIO
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (595, 842), color='white')
        draw = ImageDraw.Draw(img)
        text = f"生成预览失败: {str(e)}"
        draw.text((50, 400), text, fill='red')
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()


