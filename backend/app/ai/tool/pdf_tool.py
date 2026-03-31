from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from pydantic import BaseModel, Field
from langchain.tools import tool
import time
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# 注册CID字体（支持中文）
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))


class PdfArgs(BaseModel):
    title: str = Field(..., description="报告标题")
    sections: dict = Field(..., description="报告各部分内容，格式：{'section_title': 'content'}")


@tool(args_schema=PdfArgs)
def create_pdf(title: str, sections: dict) -> str:
    """
    生成PDF文档
    """
    try:
        # 创建PDF文件名（使用时间戳）
        timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
        filename = f"report_{timestamp}.pdf"

        # 定义保存路径
        pdf_dir = os.path.join(os.getcwd(), "static", "download")
        os.makedirs(pdf_dir, exist_ok=True)
        file_path = os.path.join(pdf_dir, filename)

        # 创建PDF文档
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # 获取样式表
        styles = getSampleStyleSheet()

        # 创建使用中文字体的样式
        # 1. 标题样式
        title_style = ParagraphStyle(
            'ChineseTitle',
            parent=styles['Title'],
            fontName='STSong-Light',  # 使用CID字体
            fontSize=18,
            spaceAfter=20,
            textColor=colors.HexColor('#2c3e50'),
            alignment=1  # 居中
        )

        # 2. 小标题样式
        heading2_style = ParagraphStyle(
            'ChineseHeading2',
            parent=styles['Heading2'],
            fontName='STSong-Light',
            fontSize=14,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor('#34495e')
        )

        # 3. 正文字体样式
        normal_style = ParagraphStyle(
            'ChineseNormal',
            parent=styles['Normal'],
            fontName='STSong-Light',
            fontSize=11,
            spaceAfter=8,
            leading=14,
            textColor=colors.HexColor('#2c3e50')
        )

        # 4. 小字体样式（用于时间等）
        small_style = ParagraphStyle(
            'ChineseSmall',
            parent=styles['Normal'],
            fontName='STSong-Light',
            fontSize=9
        )

        # 构建PDF内容
        story = []

        # 添加主标题
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 20))

        # 添加生成时间
        story.append(Paragraph(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}", small_style))
        story.append(Spacer(1, 30))

        # 添加各部分内容
        for section_title, content in sections.items():
            # 添加章节标题
            story.append(Paragraph(f"<b>{section_title}</b>", heading2_style))

            # 处理内容
            if isinstance(content, list):
                # 如果是列表，添加项目符号
                for item in content:
                    # 使用中文项目符号"·"或者保持原有
                    item_str = str(item)
                    if item_str.startswith('•'):
                        item_str = '·' + item_str[1:]  # 替换•为·
                    story.append(Paragraph(item_str, normal_style))
            elif isinstance(content, str):
                # 如果是字符串，按换行分割
                paragraphs = content.split('\n')
                for para in paragraphs:
                    if para.strip():
                        story.append(Paragraph(para, normal_style))
            else:
                # 其他类型转换为字符串
                story.append(Paragraph(str(content), normal_style))

            story.append(Spacer(1, 15))

        # 生成PDF文件
        doc.build(story)

        # 返回下载链接
        download_link = f"http://localhost:8000/static/download/{filename}"
        print(f"PDF生成成功: {download_link}")
        return download_link

    except Exception as e:
        error_msg = f"PDF生成失败: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()  # 打印详细错误信息
        return error_msg