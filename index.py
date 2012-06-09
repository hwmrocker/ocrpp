import os
import time
from datetime import datetime
from flask import Flask, render_template, url_for, request, redirect, flash
application = app = Flask(__name__)
app.secret_key = '/lkasg;izb/sijgagAGkjzxBJLhBKzKzbFKgjadgF'

def _get_chapters():
    return sorted([(d, {'url':url_for("show_chapter", chapter=d),
                        'finished':_chapter_progress(d)}) 
                    for d in os.listdir("static") 
                    if os.path.isdir(os.path.join("static",d))])

def _get_imgs(_chapter):
    return sorted([(i, {'url':url_for("show_page", chapter=_chapter, page=i),
                        'finished':_is_finished(_chapter, i, "[F]", "[ ]")})
                    for i in os.listdir(os.path.join("static", _chapter)) 
                    if i.endswith('.png')])

def _get_newest_file(chapter, page):
    filename = page.rsplit('.')[0]
    files = sorted([t for t in os.listdir(os.path.join("static", chapter)) if t.endswith('.txt') and filename in t], reverse=True)
    if len(files) > 0:
        return os.path.join("static", chapter, files[0])
    else:
        return None

def _get_text(chapter, page):
    txtfn = _get_newest_file(chapter, page)
    if txtfn:
        with open(txtfn) as inputfh:
            txt = inputfh.read().decode('utf-8')
    else:
        txt = ""
    return txt

def _chapter_progress(chapter):
    _imgs = _get_imgs(chapter)
    cnt = len([img for img, info in _imgs if info['finished'] == "[F]"])

    return "%03d/%03d" %(cnt, len(_imgs))
def _is_finished(chapter, page, astr_t='checked="checked"', astr_f=""):
    if os.path.isfile(os.path.join('static', chapter, page) + '.done'):
        return astr_t
    else:
        return astr_f

def _set_finished(chapter, page, fset=True):
    fn = os.path.join('static', chapter, page) + '.done'
    if fset:
        open(fn, 'w')
        flash("Seite als, Fertig markiert")
    else:
        try:
            os.unlink(fn)
        except:
            pass

def _get_next_page():
    maxtime = time.mktime(time.localtime()) - 15 * 60
    chapters = sorted([c for c in os.listdir("static") if os.path.isdir(os.path.join("static",c))])
    pages = []
    for c in chapters:
        pages.extend(sorted([(c,p) for p in os.listdir(os.path.join("static", c)) if p.endswith('.png') and os.path.getmtime(os.path.join("static", c, p)) < maxtime]))
        if len(pages) > 0:
            return pages[0]
    

@app.route('/')
def hello_world():
    chapters = _get_chapters()
    return render_template('index.html', chapters=chapters)

@app.route('/next')
def next_page():
    c,p = _get_next_page()
    return redirect(url_for("show_page", chapter=c, page=p))

@app.route('/kapitel/<chapter>/')
def show_chapter(chapter):
    imgs = _get_imgs(chapter)
    return render_template('index.html', chapters=imgs)
    
@app.route('/kapitel/<chapter>/<page>/save', methods=['POST'])
def save_page(chapter, page):
    txt = _get_text(chapter, page)
    new_text = request.form['text']
    if txt != new_text:
        new_filename = "%s_%s.txt" %(datetime.now().strftime('%Y%m%d%H%M%S'), page.rsplit('.',1)[0])
        with open(os.path.join('static', chapter, new_filename), 'w') as outfh:
            outfh.write(new_text.encode('utf-8'))
            flash("Seite erfolgreich gespeichert")
    f=request.form.get('finished')
    _set_finished(chapter, page, request.form.get('finished'))
    return redirect(url_for("show_page", chapter=chapter, page=page))

@app.route('/kapitel/<chapter>/<page>/', methods=['GET'])
def show_page(chapter, page):
    img = url_for("static", filename=os.path.join(chapter, page))
    txt = _get_text(chapter, page)

    finished = _is_finished(chapter, page)
    
    os.utime(os.path.join("static", chapter, page), None)

    return render_template('page.html', img=img, text=txt, finished=finished)

if __name__ == '__main__':
    app.debug = True
    app.run()
else:
    application = app
