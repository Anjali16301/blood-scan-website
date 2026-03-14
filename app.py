from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import cv2, numpy as np, os, json, threading, time, pickle, requests
from werkzeug.utils import secure_filename
import tensorflow as tf
from functools import wraps

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = os.environ.get('SECRET_KEY','blood_group_2024')

USERS = {'admin':'admin123','doctor':'doctor123','user':'user123'}
BLOOD_GROUPS = ['A+','A-','B+','B-','AB+','O+','O-']
model = None
accuracy_report = None

def download_model():
    wf = 'model_weights.pkl'
    if os.path.exists(wf):
        os.remove(wf)
        print("🗑️ Deleted old weights!")
    try:
        file_id = os.environ.get('MODEL_FILE_ID','')
        if not file_id:
            print("⚠️ MODEL_FILE_ID not set!")
            return False
        print(f"⬇️ Downloading... id={file_id}")
        try:
            import gdown
            url = f"https://drive.google.com/uc?id={file_id}&export=download&confirm=t"
            gdown.download(url, wf, quiet=False, fuzzy=True)
            if os.path.exists(wf) and os.path.getsize(wf) > 100000:
                size = os.path.getsize(wf)/(1024*1024)
                print(f"✅ gdown success! Size: {size:.1f} MB")
                return True
        except Exception as e:
            print(f"gdown failed: {e}")
        try:
            s = requests.Session()
            url = f"https://drive.google.com/uc?export=download&id={file_id}"
            r = s.get(url, stream=True, timeout=180)
            token = None
            for key, value in r.cookies.items():
                if key.startswith('download_warning'):
                    token = value
            if token:
                url = f"https://drive.google.com/uc?export=download&confirm={token}&id={file_id}"
                r = s.get(url, stream=True, timeout=180)
            with open(wf,'wb') as f:
                for chunk in r.iter_content(chunk_size=32768):
                    if chunk: f.write(chunk)
            if os.path.exists(wf) and os.path.getsize(wf) > 100000:
                size = os.path.getsize(wf)/(1024*1024)
                print(f"✅ requests success! Size: {size:.1f} MB")
                return True
        except Exception as e:
            print(f"requests failed: {e}")
        return False
    except Exception as e:
        print(f"Download error: {e}")
        return False

def build_model():
    inp = tf.keras.Input(shape=(96,96,1))
    x = tf.keras.layers.Conv2D(32,(3,3),padding='same',activation='relu')(inp)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Conv2D(32,(3,3),padding='same',activation='relu')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.MaxPooling2D(2,2)(x)
    x = tf.keras.layers.Dropout(0.25)(x)
    x = tf.keras.layers.Conv2D(64,(3,3),padding='same',activation='relu')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Conv2D(64,(3,3),padding='same',activation='relu')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.MaxPooling2D(2,2)(x)
    x = tf.keras.layers.Dropout(0.25)(x)
    x = tf.keras.layers.Conv2D(128,(3,3),padding='same',activation='relu')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Conv2D(128,(3,3),padding='same',activation='relu')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.MaxPooling2D(2,2)(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    x = tf.keras.layers.Conv2D(256,(3,3),padding='same',activation='relu')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Conv2D(256,(3,3),padding='same',activation='relu')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.MaxPooling2D(2,2)(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(512,activation='relu')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.5)(x)
    x = tf.keras.layers.Dense(256,activation='relu')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.4)(x)
    out = tf.keras.layers.Dense(len(BLOOD_GROUPS),activation='softmax')(x)
    return tf.keras.Model(inputs=inp, outputs=out)

def startup_load():
    global model, accuracy_report
    try:
        download_model()
        wf = 'model_weights.pkl'
        if os.path.exists(wf):
            size = os.path.getsize(wf)/(1024*1024)
            print(f"📦 Building model... {size:.1f} MB")
            model = build_model()
            with open(wf,'rb') as f:
                weights_safe = pickle.load(f)
            weights = []
            for w in weights_safe:
                arr = np.frombuffer(w['data'], dtype=w['dtype'])
                arr = arr.reshape(w['shape'])
                weights.append(arr)
            print(f"📊 Arrays: {len(weights)}")
            model.set_weights(weights)
            test = np.zeros((1,96,96,1))
            pred = model.predict(test, verbose=0)
            print(f"✅ Model ready! Max: {np.max(pred[0])*100:.1f}%")
        else:
            print("⚠️ No weights file found!")
        if os.path.exists('accuracy_report.json'):
            with open('accuracy_report.json') as f:
                accuracy_report = json.load(f)
            print(f"✅ Report loaded! {accuracy_report.get('test_accuracy')}%")
        else:
            print("⚠️ No accuracy_report.json found!")
    except Exception as e:
        print(f"❌ Startup error: {e}")
        import traceback
        traceback.print_exc()

startup_load()

def keep_alive():
    time.sleep(120)
    while True:
        try:
            import urllib.request
            url = os.environ.get('APP_URL','')
            if url:
                urllib.request.urlopen(f'{url}/ping', timeout=10)
                print("✅ Keep-alive ping sent")
        except: pass
        time.sleep(840)

threading.Thread(target=keep_alive, daemon=True).start()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def preprocess(path):
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray,(96,96))
    eq = cv2.equalizeHist(resized)
    return (eq/255.0).reshape(1,96,96,1)

def extract_features(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    blur = cv2.GaussianBlur(cv2.equalizeHist(img),(5,5),0)
    edges = cv2.Canny(blur, 50, 150)
    rc = int(np.sum(edges > 0))
    _,binary = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    contours,_ = cv2.findContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    pattern = 'Arch' if rc<50000 else 'Loop' if rc<100000 else 'Whorl'
    return {'ridge_count':rc,'minutiae_count':len(contours),'pattern_type':pattern}

@app.route('/')
def home():
    return redirect(url_for('dashboard') if 'logged_in' in session else url_for('login'))

@app.route('/ping')
def ping():
    return 'ok', 200

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username','').strip()
        p = request.form.get('password','').strip()
        if u in USERS and USERS[u] == p:
            session['logged_in'] = True
            session['username'] = u
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html',
                           username=session.get('username'),
                           report=accuracy_report)

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    global model
    if model is None:
        return jsonify({'success':False,'error':'Model not loaded.'}), 500
    if 'fingerprint' not in request.files:
        return jsonify({'error':'No file uploaded'}), 400
    file = request.files['fingerprint']
    if file.filename == '':
        return jsonify({'error':'No file selected'}), 400
    filename = secure_filename(file.filename)
    os.makedirs('uploads', exist_ok=True)
    filepath = os.path.join('uploads', filename)
    file.save(filepath)
    try:
        processed = preprocess(filepath)
        features = extract_features(filepath)
        pred = model.predict(processed, verbose=0)
        idx = int(np.argmax(pred[0]))
        conf = float(pred[0][idx]) * 100
        probs = {bg:round(float(pred[0][i])*100,2)
                 for i,bg in enumerate(BLOOD_GROUPS)}
        os.remove(filepath)
        return jsonify({
            'success':True,
            'blood_group':BLOOD_GROUPS[idx],
            'confidence':round(conf,2),
            'probabilities':probs,
            'features':features
        })
    except Exception as e:
        if os.path.exists(filepath): os.remove(filepath)
        return jsonify({'error':str(e),'success':False}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
