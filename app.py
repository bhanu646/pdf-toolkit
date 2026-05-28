import os
import uuid
from flask import Flask, render_template, request, jsonify, send_file
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/pdftk_uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/merge', methods=['POST'])
def merge_pdfs():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400

        files = request.files.getlist('files')
        if len(files) < 2:
            return jsonify({'error': 'At least 2 PDF files required'}), 400

        merger = PdfMerger()
        temp_files = []

        for file in files:
            if file and file.filename.lower().endswith('.pdf'):
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}.pdf")
                file.save(temp_path)
                temp_files.append(temp_path)
                merger.append(temp_path)

        output_filename = f"merged_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        merger.write(output_path)
        merger.close()

        for tf in temp_files:
            try: os.remove(tf)
            except: pass

        file_size = os.path.getsize(output_path)

        return jsonify({
            'success': True,
            'filename': output_filename,
            'download_url': f'/download/{output_filename}',
            'file_size': file_size,
            'files_merged': len(files)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/split', methods=['POST'])
def split_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Invalid file'}), 400

        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}.pdf")
        file.save(input_path)

        reader = PdfReader(input_path)
        total_pages = len(reader.pages)

        start_page = int(request.form.get('start_page', 1)) - 1
        end_page = int(request.form.get('end_page', total_pages)) - 1

        if start_page < 0 or end_page >= total_pages or start_page > end_page:
            os.remove(input_path)
            return jsonify({'error': 'Invalid page range'}), 400

        writer = PdfWriter()
        for i in range(start_page, end_page + 1):
            writer.add_page(reader.pages[i])

        output_filename = f"split_{start_page + 1}_to_{end_page + 1}_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        file_size = os.path.getsize(output_path)
        os.remove(input_path)

        return jsonify({
            'success': True,
            'filename': output_filename,
            'download_url': f'/download/{output_filename}',
            'file_size': file_size,
            'pages_extracted': end_page - start_page + 1,
            'total_pages': total_pages
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/extract-pages', methods=['POST'])
def extract_pages():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Invalid file'}), 400

        pages_to_extract = request.form.get('pages', '')
        if not pages_to_extract:
            return jsonify({'error': 'Please specify pages to extract'}), 400

        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}.pdf")
        file.save(input_path)

        reader = PdfReader(input_path)
        total_pages = len(reader.pages)

        extract_indices = []
        for p in pages_to_extract.split(','):
            try:
                idx = int(p.strip()) - 1
                if 0 <= idx < total_pages:
                    extract_indices.append(idx)
            except:
                pass

        writer = PdfWriter()
        for idx in extract_indices:
            writer.add_page(reader.pages[idx])

        output_filename = f"extracted_pages_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        file_size = os.path.getsize(output_path)
        os.remove(input_path)

        return jsonify({
            'success': True,
            'filename': output_filename,
            'download_url': f'/download/{output_filename}',
            'file_size': file_size,
            'pages_extracted': len(extract_indices)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/remove-pages', methods=['POST'])
def remove_pages():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Invalid file'}), 400

        pages_to_remove = request.form.get('pages', '')
        if not pages_to_remove:
            return jsonify({'error': 'Please specify pages to remove'}), 400

        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}.pdf")
        file.save(input_path)

        reader = PdfReader(input_path)
        total_pages = len(reader.pages)

        remove_indices = set()
        for p in pages_to_remove.split(','):
            try:
                idx = int(p.strip()) - 1
                if 0 <= idx < total_pages:
                    remove_indices.add(idx)
            except:
                pass

        writer = PdfWriter()
        remaining = 0
        for i in range(total_pages):
            if i not in remove_indices:
                writer.add_page(reader.pages[i])
                remaining += 1

        output_filename = f"removed_pages_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        file_size = os.path.getsize(output_path)
        os.remove(input_path)

        return jsonify({
            'success': True,
            'filename': output_filename,
            'download_url': f'/download/{output_filename}',
            'file_size': file_size,
            'pages_removed': len(remove_indices),
            'pages_remaining': remaining
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/rotate', methods=['POST'])
def rotate_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Invalid file'}), 400

        angle = int(request.form.get('angle', 90))
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}.pdf")
        file.save(input_path)

        reader = PdfReader(input_path)
        writer = PdfWriter()

        for page in reader.pages:
            page.rotate(angle)
            writer.add_page(page)

        output_filename = f"rotated_{angle}deg_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        file_size = os.path.getsize(output_path)
        os.remove(input_path)

        return jsonify({
            'success': True,
            'filename': output_filename,
            'download_url': f'/download/{output_filename}',
            'file_size': file_size,
            'pages_rotated': len(reader.pages)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/resize', methods=['POST'])
def resize_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Invalid file'}), 400

        page_size = request.form.get('page_size', 'A4')
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}.pdf")
        file.save(input_path)

        reader = PdfReader(input_path)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        output_filename = f"resized_{page_size}_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        file_size = os.path.getsize(output_path)
        os.remove(input_path)

        return jsonify({
            'success': True,
            'filename': output_filename,
            'download_url': f'/download/{output_filename}',
            'file_size': file_size,
            'page_size': page_size,
            'pages': len(reader.pages)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/compress', methods=['POST'])
def compress_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Invalid file'}), 400

        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}.pdf")
        file.save(input_path)

        input_size = os.path.getsize(input_path)

        reader = PdfReader(input_path)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        output_filename = f"compressed_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        output_size = os.path.getsize(output_path)
        os.remove(input_path)

        savings = ((input_size - output_size) / input_size * 100) if input_size > 0 else 0

        return jsonify({
            'success': True,
            'filename': output_filename,
            'download_url': f'/download/{output_filename}',
            'file_size': output_size,
            'original_size': input_size,
            'compressed_size': output_size,
            'savings_percent': round(savings, 1),
            'pages': len(reader.pages)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/pdf-info', methods=['POST'])
def get_pdf_info():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Invalid file'}), 400

        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}.pdf")
        file.save(input_path)

        reader = PdfReader(input_path)
        size = os.path.getsize(input_path)

        info = {
            'success': True,
            'filename': file.filename,
            'pages': len(reader.pages),
            'size': size,
            'encrypted': reader.is_encrypted
        }

        if reader.metadata:
            info['metadata'] = {
                'title': str(reader.metadata.get('/Title', 'N/A')) if reader.metadata.get('/Title') else 'N/A',
                'author': str(reader.metadata.get('/Author', 'N/A')) if reader.metadata.get('/Author') else 'N/A',
            }

        os.remove(input_path)
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/protect', methods=['POST'])
def protect_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        password = request.form.get('password', '')

        if not file.filename.lower().endswith('.pdf') or not password:
            return jsonify({'error': 'Password is required'}), 400

        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}.pdf")
        file.save(input_path)

        reader = PdfReader(input_path)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.encrypt(password)

        output_filename = f"protected_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        file_size = os.path.getsize(output_path)
        os.remove(input_path)

        return jsonify({
            'success': True,
            'filename': output_filename,
            'download_url': f'/download/{output_filename}',
            'file_size': file_size,
            'protected': True
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/unlock', methods=['POST'])
def unlock_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        password = request.form.get('password', '')

        if not file.filename.lower().endswith('.pdf') or not password:
            return jsonify({'error': 'Password is required'}), 400

        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}.pdf")
        file.save(input_path)

        reader = PdfReader(input_path)

        if not reader.is_encrypted:
            os.remove(input_path)
            return jsonify({'error': 'PDF is not encrypted'}), 400

        reader.decrypt(password)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        output_filename = f"unlocked_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        file_size = os.path.getsize(output_path)
        os.remove(input_path)

        return jsonify({
            'success': True,
            'filename': output_filename,
            'download_url': f'/download/{output_filename}',
            'file_size': file_size,
            'unlocked': True
        })
    except Exception as e:
        return jsonify({'error': 'Invalid password'}), 400


@app.route('/api/image-to-pdf', methods=['POST'])
def image_to_pdf():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400

        files = request.files.getlist('files')
        if len(files) < 1:
            return jsonify({'error': 'At least 1 image required'}), 400

        images = []
        for file in files:
            if file and file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                img = Image.open(file).convert('RGB')
                images.append(img)

        if not images:
            return jsonify({'error': 'No valid images found'}), 400

        output_filename = f"images_to_pdf_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        if len(images) == 1:
            images[0].save(output_path, 'PDF')
        else:
            images[0].save(output_path, save_all=True, append_images=images[1:], resolution=100.0)

        file_size = os.path.getsize(output_path)

        return jsonify({
            'success': True,
            'filename': output_filename,
            'download_url': f'/download/{output_filename}',
            'file_size': file_size,
            'total_images': len(images)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/extract-text', methods=['POST'])
def extract_text():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Invalid file'}), 400

        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}.pdf")
        file.save(input_path)

        reader = PdfReader(input_path)
        total_pages = len(reader.pages)

        full_text = ""
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                full_text += f"\n--- Page {page_num + 1} ---\n{text}"

        os.remove(input_path)

        return jsonify({
            'success': True,
            'text': full_text.strip(),
            'total_pages': total_pages,
            'word_count': len(full_text.split()),
            'char_count': len(full_text)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<path:filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)